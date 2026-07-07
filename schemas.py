from pydantic import BaseModel, Field
from typing import List

class CodeRequest(BaseModel):
    code: str = Field(..., description="The source code to analyze")
    language: str = Field(default="python", description="Programming language")

class RiskFinding(BaseModel):
    line_number: int
    issue: str
    severity: str
    category: str

class RiskResponse(BaseModel):
    risk_score: float
    findings: List[RiskFinding]
    summary: str
