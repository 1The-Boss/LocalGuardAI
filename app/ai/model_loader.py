import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "priority_model.pkl"

def load_model():
    vectorizer, model = joblib.load(MODEL_PATH)
    return vectorizer, model