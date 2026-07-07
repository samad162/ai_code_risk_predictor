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

Note: On the first run, the app will download the CodeBERT AI model (~500MB) from HuggingFace. If you lack internet, it will gracefully fall back to static AST/Regex analysis.
