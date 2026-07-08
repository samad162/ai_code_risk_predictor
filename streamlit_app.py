import streamlit as st

from core.analyzer import RiskPredictorEngine


SAMPLE_CODE = """import os

password = "super-secret"
user_input = input("Command: ")
os.system(user_input)
"""


@st.cache_resource(show_spinner="Loading risk analysis engine...")
def get_engine() -> RiskPredictorEngine:
    """Create one analyzer instance per Streamlit worker process."""
    return RiskPredictorEngine()


def severity_badge(severity: str) -> str:
    colors = {
        "Critical": "#ff4b4b",
        "High": "#ff9f1c",
        "Medium": "#f9c74f",
        "Low": "#43aa8b",
    }
    return colors.get(severity, "#8d99ae")


st.set_page_config(
    page_title="AI Code Risk Predictor",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ AI Code Risk Predictor")
st.caption("Paste source code, choose a language, and scan for risky patterns before you ship.")

engine = get_engine()

with st.sidebar:
    st.header("Settings")
    language = st.selectbox(
        "Language",
        options=["python", "javascript", "typescript", "java", "go", "ruby", "php", "csharp", "other"],
        index=0,
    )
    st.divider()
    st.write("**Engine status**")
    if engine.ai_loaded:
        st.success("Groq AI enabled")
    else:
        st.info("Static analysis mode")
    st.caption("Add `GROQ_API_KEY` in Streamlit secrets to enable AI scoring.")

left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.subheader("Source code")
    code = st.text_area(
        "Code to analyze",
        value=SAMPLE_CODE,
        height=460,
        label_visibility="collapsed",
    )
    scan = st.button("Scan code", type="primary", use_container_width=True)

with right:
    st.subheader("Risk report")
    if scan:
        if not code.strip():
            st.warning("Paste some code before scanning.")
        else:
            with st.spinner("Analyzing code..."):
                result = engine.analyze(code=code, language=language)

            score_percent = result.risk_score * 100
            st.metric("Risk score", f"{score_percent:.1f}%")
            if result.risk_score > 0.75:
                st.error(result.summary)
            elif result.risk_score > 0.4:
                st.warning(result.summary)
            else:
                st.success(result.summary)

            if result.findings:
                st.write("### Findings")
                for finding in result.findings:
                    color = severity_badge(finding.severity)
                    st.markdown(
                        f"""
                        <div style="border-left: 5px solid {color}; padding: 0.75rem 1rem; margin-bottom: 0.75rem; border-radius: 0.35rem; background: rgba(128, 128, 128, 0.08);">
                            <strong>Line {finding.line_number}</strong> · <span style="color: {color}; font-weight: 700;">{finding.severity}</span><br>
                            {finding.issue}<br>
                            <small>Category: {finding.category}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No static vulnerabilities found.")
    else:
        st.info("Run a scan to see the vulnerability report.")
