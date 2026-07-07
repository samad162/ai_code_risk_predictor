import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from core.analyzer import RiskPredictorEngine
from schemas import CodeRequest, RiskResponse

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="AI Code Risk Predictor", version="2.0.0")

# Initialize Engine globally on startup
logger.info("Initializing Risk Prediction Engine...")
engine = RiskPredictorEngine()
logger.info("Engine ready.")

@app.get("/", response_class=HTMLResponse)
def get_ui():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        logger.error(f"Failed to load UI: {e}")
        return HTMLResponse(content="<h1>Error loading UI</h1>", status_code=500)

@app.get("/health")
def health_check():
    return {"status": "online", "ai_loaded": engine.ai_loaded}

@app.post("/predict", response_model=RiskResponse)
async def predict_risk(request: CodeRequest):
    if not request.code.strip():
        return RiskResponse(risk_score=0.0, findings=[], summary="Empty code provided.")
    
    try:
        result = engine.analyze(code=request.code, language=request.language)
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during analysis.")
