"""
Training Script for Multi-Class Expense Categorizer
Loads processed transaction corpus, trains TF-IDF + LogisticRegression model,
evaluates test performance, and saves serialized weights.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import MODELS_DIR, PROCESSED_DATA_DIR
from src.ml.classifier import TransactionClassifier
from src.ml.model_evaluator import ModelEvaluator


def main():
    print("=" * 60)
    print("Training SpendWise Transaction Auto-Categorizer")
    print("=" * 60)

    dataset_path = PROCESSED_DATA_DIR / "cleaned_transactions.csv"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df)} transactions from {dataset_path}")

    # Use narration or merchant as feature, category as label
    X = df["narration"].fillna(df["merchant"]).astype(str).tolist()
    y = df["category"].astype(str).tolist()

    # Train / Test Split (80% Train, 20% Holdout Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Split: {len(X_train)} train samples, {len(X_test)} test samples")

    # Initialize and train
    classifier = TransactionClassifier(confidence_threshold=0.30)
    classifier.fit(X_train, y_train)

    # Evaluate on test set
    predictions = classifier.predict_batch(X_test)
    y_pred = [p[0] for p in predictions]

    metrics = ModelEvaluator.evaluate(y_test, y_pred)
    print("\n--- Model Performance on Holdout Test Set ---")
    print(f"Accuracy:    {metrics['accuracy'] * 100:.2f}%")
    print(f"Macro F1:    {metrics['macro_f1']:.4f}")
    print(f"Weighted F1: {metrics['weighted_f1']:.4f}")
    print("\nDetailed Classification Report:")
    print(metrics["classification_report_text"])

    # Persist model
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    classifier.save(MODELS_DIR / "expense_classifier.joblib")
    print("Training and serialization completed successfully!")


if __name__ == "__main__":
    main()
