# Goal Detector (Streamlit MVP)

Goal Detector helps users discover and plan goals based on their interests via a short questionnaire. It turns answers into 3–5 goal suggestions with first steps, making learning and planning more accessible for students, career changers, and self-learners.

## Core Flow
Signup (optional) → Questionnaire → Matching + (optional) AI personalization → Results (goal cards)

## Run Locally
1) Create a virtual environment (recommended)
2) Install dependencies:
   - `pip install -r requirements.txt`
3) (Optional) enable AI personalization by setting `OPENAI_API_KEY` in your environment or a `.env` file.
4) Start the app:
   - `streamlit run app.py`

## Files
- `app.py`: Streamlit UI + flow
- `utils.py`: goal loading + theme extraction + scoring + optional OpenAI personalization
- `goals.json`: goal templates (acts like a tiny database)
- `PROJECT.md`: pitch, features, sample questions/goals, UX flow

## Notes (MVP)
- No database: responses are kept in Streamlit session only.
- Suggestions are educational and general (not medical/financial advice).

