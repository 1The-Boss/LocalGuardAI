from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

#Temporary
texts = [
    "fire in building",
    "water leakage",
    "road pothole",
    "major accident on highway",
    "electric short circuit"
]

labels = [10, 5, 3, 10, 7]  # priority scores

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

joblib.dump((vectorizer, model), "priority_model.pkl")