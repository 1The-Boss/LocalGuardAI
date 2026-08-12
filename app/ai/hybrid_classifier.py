from ..ai.category_classifier import classify_complaint_llm, fast_classify

CONFIDENCE_THRESHOLD = 0.65

async def classify(text: str, existing_categories: list[str]) -> dict:
    label, confidence = fast_classify(text)

    if confidence >= CONFIDENCE_THRESHOLD:
        return {"category": label, "urgency": "medium", "source": "local_model", "confidence": confidence}

    llm_result = classify_complaint_llm(text, existing_categories)
    llm_result["source"] = "llm_fallback"
    llm_result["confidence"] = confidence  # keep local model's low score for logging/audit
    return llm_result