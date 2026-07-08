# AI Code Risk Predictor

## Setup Instructions
1. Unzip this directory.
2. Open your terminal and navigate to the unzipped folder.
3. Create a virtual environment: `python -m venv venv`
4. Activate it: 
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run the server: `uvicorn main:app --reload`
7. Open your browser and go to: `http://localhost:8000`

Note: The app runs deterministic static AST/Regex analysis by default. Add a `GROQ_API_KEY` environment variable or Streamlit secret to enable AI-assisted scoring.
## Streamlit Cloud Deployment
1. Push this repository to GitHub.
2. In Streamlit Community Cloud, choose **New app** and select this repository.
3. Set the main file path to `streamlit_app.py`.
4. Optional: add `GROQ_API_KEY` under **App settings → Secrets** to enable AI-assisted scoring. Without it, the app still runs with deterministic static analysis.
5. Deploy the app.

## Local Streamlit Run
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

