# Briefly AI — Text Summarizer

Task 3 implementation: accepts long text, generates a short summary, displays original and summary, provides a simple UI, and uses local NLP plus optional Groq AI.

## Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run_checks.py
streamlit run app.py
```

## Accuracy
The local engine and percentage calculations are deterministic. AI output is advisory and should be compared with the source.

## Compression formula
`(1 - summary_words / original_words) * 100`
