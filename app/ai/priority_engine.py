from app.ai.model_loader import load_model

vectorizer, model = load_model()


def predict_priority(description: str) -> float:
    """
    Predict priority score using trained model.
    """
    X = vectorizer.transform([description])
    prediction = model.predict(X)[0]

    return float(prediction)