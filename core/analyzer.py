import ast
import re
import logging
from typing import List
from schemas import RiskFinding, RiskResponse

logger = logging.getLogger(__name__)

GROQ_API_KEY = "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"

class RiskPredictorEngine:
    def __init__(self):
        self.ai_loaded = False
        self.groq_client = None
        
        try:
            from groq import Groq
            self.groq_client = Groq(api_key=GROQ_API_KEY)
            self.ai_loaded = True
            logger.info("Groq AI client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client. Falling back to static analysis only. Error: {e}")

        # Regex patterns for multi-language static analysis
        self.risk_patterns = {
            "eval_usage": (r'\beval\s*\(', "Critical", "Use of eval() detected. Leads to arbitrary code execution."),
            "exec_usage": (r'\bexec\s*\(', "Critical", "Use of exec() detected. Leads to arbitrary code execution."),
            "shell_true": (r'shell\s*=\s*True', "High", "Subprocess with shell=True is vulnerable to injection."),
            "os_system": (r'os\.system\s*\(', "High", "os.system is vulnerable to command injection."),
            "hardcoded_secret": (r'(password|passwd|secret|api_key|token)\s*=\s*["\']', "High", "Hardcoded secret detected."),
            "pickle_load": (r'pickle\.loads?\s*\(', "High", "Pickle deserialization can execute arbitrary code."),
            "sql_injection": (r'(SELECT|INSERT|UPDATE|DELETE).*\+.*', "Medium", "Possible SQL injection via string concatenation.")
        }

    def _get_ai_risk_score(self, code: str) -> float:
        if not self.ai_loaded or not self.groq_client:
            return 0.0
        try:
            prompt = f"""Analyze the following code for security vulnerabilities. 
Return ONLY a JSON object with a single key "risk_score" containing a float between 0.0 (no risk) and 1.0 (critical risk).
Do not include any explanation, just the JSON.

Code:
```
{code}
```

Response:"""

            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=100,
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            import json
            import re
            json_match = re.search(r'\{[^}]*"risk_score"\s*:\s*([0-9.]+)[^}]*\}', response_text)
            if json_match:
                score = float(json_match.group(1))
                return min(max(score, 0.0), 1.0)
            
            return 0.0
        except Exception as e:
            logger.warning(f"AI inference failed: {e}")
            return 0.0

    def _static_analysis(self, code: str, language: str) -> List[RiskFinding]:
        findings = []
        lines = code.split('\n')
        
        # 1. Regex Analysis (Works on all languages)
        # For Python, eval()/exec() are already caught precisely by the AST
        # pass below, so skip them here to avoid duplicate findings.
        ast_handled_patterns = {"eval_usage", "exec_usage"} if language.lower() == "python" else set()

        for i, line in enumerate(lines, 1):
            for pattern_name, (regex, severity, desc) in self.risk_patterns.items():
                if pattern_name in ast_handled_patterns:
                    continue
                if re.search(regex, line, re.IGNORECASE):
                    findings.append(RiskFinding(
                        line_number=i, issue=desc, severity=severity, category="Static_Regex"
                    ))

        # 2. Python AST Analysis (Deterministic, zero hallucination)
        if language.lower() == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec', '__import__'):
                            findings.append(RiskFinding(
                                line_number=node.lineno,
                                issue=f"AST detected dangerous call: {node.func.id}()",
                                severity="Critical",
                                category="Static_AST"
                            ))
            except SyntaxError:
                logger.info("AST parsing failed due to syntax error. Relying on Regex and AI.")
            except Exception as e:
                logger.warning(f"AST analysis error: {e}")
                
        return findings

    def analyze(self, code: str, language: str) -> RiskResponse:
        # Run Static Analysis
        static_findings = self._static_analysis(code, language)
        
        # Run AI Analysis
        ai_risk_score = self._get_ai_risk_score(code)
        
        # Calculate Static Risk Score based on findings
        static_risk_score = 0.0
        if any(f.severity == "Critical" for f in static_findings):
            static_risk_score = 1.0
        elif any(f.severity == "High" for f in static_findings):
            static_risk_score = 0.7
        elif any(f.severity == "Medium" for f in static_findings):
            static_risk_score = 0.4

        # Combine scores: Take the maximum to avoid false negatives
        final_risk_score = max(ai_risk_score, static_risk_score)
        
        # Generate Summary
        if final_risk_score > 0.75:
            summary = "CRITICAL RISK: High probability of severe vulnerabilities detected."
        elif final_risk_score > 0.4:
            summary = "MODERATE RISK: Potential security issues found. Review required."
        else:
            summary = "LOW RISK: No major vulnerabilities detected."

        return RiskResponse(
            risk_score=round(final_risk_score, 4),
            findings=static_findings,
            summary=summary
        )
