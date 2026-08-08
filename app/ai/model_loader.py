import joblib

def load_model():
    vectorizer, model = joblib.load("priority_model.pkl")
    return vectorizer, model