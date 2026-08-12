from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, pipeline
import torch
import os, json
from groq import Groq
from huggingface_hub import login
from datasets import Dataset
login(token=os.getenv("HF_TOKEN"))

CATEGORIES = [
    "road", "water", "garbage", "electricity", "sanitation",
    "stray_animals", "public_safety", "public_services", "public_transport",
    "illegal_construction", "corruption", "misinformation", "noise",
    "parks_environment", "public_health", "other"
]
model_name = "ai4bharat/IndicBERT-v3-270M"
fine_tuned_dir = "./indicbert-category-classifier"

# Try to load fine-tuned model first, fall back to base model
try:
    tokenizer = AutoTokenizer.from_pretrained(fine_tuned_dir)
    model = AutoModelForSequenceClassification.from_pretrained(
        fine_tuned_dir,
        num_labels=len(CATEGORIES),
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    )
    print(f"Loaded fine-tuned model from {fine_tuned_dir}")
except Exception:
    print(f"Fine-tuned model not found at {fine_tuned_dir}, loading base model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(CATEGORIES),
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    )

classifier = pipeline(
    "text-classification", 
    model=model, 
    tokenizer=tokenizer,
    top_k=4,
    function_to_apply="softmax"
    )

def fast_classify(text: str) -> tuple[str, float]:
    result = classifier(text)
    if not result:
        return "other", 0.0
    # Handle pipeline output: can be list of dicts (with top_k) or single dict
    if isinstance(result, list) and len(result) > 0:
        first_result = result[0]
        # If first_result is also a list, get its first element
        if isinstance(first_result, list) and len(first_result) > 0:
            first_result = first_result[0]
    else:
        first_result = result
    # Ensure first_result is a dict
    if not isinstance(first_result, dict):
        return "other", 0.0
    label = first_result.get("label", "other")
    score = first_result.get("score", 0.0)
    
    # Map label index to category name (e.g., LABEL_0 -> road)
    if label.startswith("LABEL_"):
        try:
            idx = int(label.split("_")[1])
            if 0 <= idx < len(CATEGORIES):
                label = CATEGORIES[idx]
            else:
                label = "other"
        except (ValueError, IndexError):
            label = "other"
    
    return label, score 



def tokenize_fn(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=128)


def fine_tune_model(train_texts: list[str], train_labels: list[int], test_texts: list[str] = None, test_labels: list[int] = None):
    """
    Fine-tune the IndicBERT model on your complaint dataset.
    
    Args:
        train_texts: List of complaint texts for training
        train_labels: List of label indices (0-15 for 16 categories)
        test_texts: Optional list of complaint texts for evaluation
        test_labels: Optional list of label indices for evaluation
    """
    # Create dataset
    train_data = {"text": train_texts, "label": train_labels}
    train_dataset = Dataset.from_dict(train_data)
    
    tokenized_train = train_dataset.map(tokenize_fn, batched=True)
    
    eval_dataset = None
    if test_texts and test_labels:
        test_data = {"text": test_texts, "label": test_labels}
        test_dataset = Dataset.from_dict(test_data)
        eval_dataset = test_dataset.map(tokenize_fn, batched=True)
    
    args = TrainingArguments(
        output_dir="./indicbert-category-classifier",
        per_device_train_batch_size=8,
        num_train_epochs=3,
        learning_rate=2e-5,
        save_strategy="epoch",
        eval_strategy="epoch",
        logging_strategy="epoch"
    )
    
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized_train,
        eval_dataset=eval_dataset
    )
    trainer.train()
    trainer.save_model("./indicbert-category-classifier")
    return trainer


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# few-shot examples pulled from your actual fine-tuning set — keeps LLM anchored to real taxonomy
FEW_SHOT_EXAMPLES = """Examples:
Complaint: "Streetlight near the temple has been off for a week" → category: electricity, reason: lighting infrastructure fault
Complaint: "Dogs chasing kids near the school gate" → category: stray_animals, reason: new category, not covered by existing set
Complaint: "Sewage overflowing onto the main road" → category: sanitation, reason: waste/sewage issue despite mentioning road
"""

def classify_complaint_llm(text: str, existing_categories: list[str]) -> dict:
    existing_list = ", ".join(existing_categories) if existing_categories else "(none yet)"

    prompt = f"""You are categorizing civic complaints for a local governance platform.

Existing categories in use: {existing_list}

{FEW_SHOT_EXAMPLES}

Now classify this complaint. Think step by step: first identify the core issue, then check if an existing category truly fits, then decide.

Complaint: "{text}"

Respond ONLY with valid JSON:
{{"reasoning": "...", "category": "...", "is_new_category": true/false, "urgency": "low|medium|high"}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM classification failed: {e}")
        return {
            "category": "uncategorized",
            "is_new_category": True,
            "urgency": "medium",
            "reasoning": "parse_error"
        }


def generate_citizen_response(description: str, category: str, status: str) -> str:
    """LLM-generated public-facing acknowledgment — the 'AI-assisted public communication' feature."""
    prompt = f"""Write a short, respectful acknowledgment message (2-3 sentences) to a citizen who filed this complaint.

Complaint: "{description}"
Category: {category}
Status: {status}

Tone: professional, reassuring, no bureaucratic jargon. Do not make promises about exact timelines."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Failed to generate response: {e}")
        return "Thank you for your complaint. We will review it shortly."