"""
Fine-tune the IndicBERT model on the sample complaints dataset.
Run this script to train the model before using it for classification.
"""
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.ai.category_classifier import fine_tune_model, CATEGORIES

def load_training_data(file_path: str = None):
    """Load training data from JSON file."""
    if file_path is None:
        file_path = Path(__file__).parent.parent / "data" / "sample_complaints.json"
    
    with open(file_path, encoding="utf-8") as f:
        complaints = json.load(f)
    
    # Extract texts and labels
    train_texts = []
    train_labels = []
    
    for c in complaints:
        text = c.get("text", "")
        category = c.get("expected_category", "other")
        
        # Map category string to index
        if category in CATEGORIES:
            label_idx = CATEGORIES.index(category)
        else:
            # Map to "other" if not in our categories
            label_idx = CATEGORIES.index("other")
        
        train_texts.append(text)
        train_labels.append(label_idx)
    
    return train_texts, train_labels

def main():
    print("Loading training data...")
    train_texts, train_labels = load_training_data()
    
    print(f"Loaded {len(train_texts)} training examples")
    print(f"Categories: {CATEGORIES}")
    print(f"Number of categories: {len(CATEGORIES)}")
    
    # Split into train and test (80/20)
    split_idx = int(len(train_texts) * 0.8)
    train_texts_split = train_texts[:split_idx]
    train_labels_split = train_labels[:split_idx]
    test_texts = train_texts[split_idx:]
    test_labels = train_labels[split_idx:]
    
    print(f"Training on {len(train_texts_split)} examples")
    print(f"Testing on {len(test_texts)} examples")
    
    print("\nStarting fine-tuning...")
    trainer = fine_tune_model(
        train_texts=train_texts_split,
        train_labels=train_labels_split,
        test_texts=test_texts,
        test_labels=test_labels
    )
    
    print("\nFine-tuning complete!")
    print(f"Model saved to: ./indicbert-category-classifier")
    print(f"You can now load the fine-tuned model for classification.")

if __name__ == "__main__":
    main()
