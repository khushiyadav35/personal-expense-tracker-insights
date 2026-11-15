"""
Hybrid Machine Learning Transaction Classifier
Combines rule-based keyword matching with a TF-IDF + Calibrated Linear Model.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.config import CATEGORIES, MERCHANT_KEYWORDS, MODELS_DIR
from src.ml.text_preprocessor import TransactionTextPreprocessor


class TransactionClassifier:
    """Hybrid Classifier for Expense and Income Categorization."""

    def __init__(self, confidence_threshold: float = 0.35):
        self.confidence_threshold = confidence_threshold
        self.user_overrides: Dict[str, str] = {}
        self.preprocessor = TransactionTextPreprocessor()

        # Build pipeline: TF-IDF + Logistic Regression
        self.pipeline: Optional[Pipeline] = None
        self.is_trained = False

    def _rule_based_predict(self, text: str) -> Optional[Tuple[str, float]]:
        """Checks if text matches known merchant keywords with 100% confidence."""
        clean = self.preprocessor.clean_text(text)

        # Check user manual overrides first
        for key, cat in self.user_overrides.items():
            if key in clean:
                return cat, 1.0

        # Check domain merchant taxonomy
        for cat, keywords in MERCHANT_KEYWORDS.items():
            for kw in keywords:
                # Word boundary or clean substring
                if f" {kw} " in f" {clean} " or clean == kw:
                    return cat, 0.98

        return None

    def fit(self, texts: List[str], labels: List[str]):
        """Trains the TF-IDF and Logistic Regression classification pipeline."""
        cleaned_texts = self.preprocessor.clean_batch(texts)

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1,
                max_features=2500
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=2.0,
                class_weight="balanced",
                random_state=42
            ))
        ])

        self.pipeline.fit(cleaned_texts, labels)
        self.is_trained = True
        return self

    def predict_single(self, text: str) -> Tuple[str, float, str]:
        """
        Predicts category, confidence score, and prediction method.
        Returns: (predicted_category, confidence_score, method: 'Rule' | 'ML' | 'Fallback')
        """
        # 1. Fast Rule-Based Lookup
        rule_res = self._rule_based_predict(text)
        if rule_res:
            return rule_res[0], rule_res[1], "Rule-Based Heuristic"

        # 2. ML Prediction
        if self.is_trained and self.pipeline is not None:
            clean = self.preprocessor.clean_text(text)
            if not clean:
                return "Other / Miscellaneous", 0.30, "Fallback Default"

            probs = self.pipeline.predict_proba([clean])[0]
            classes = self.pipeline.classes_
            max_idx = int(np.argmax(probs))
            best_cat = str(classes[max_idx])
            best_prob = float(probs[max_idx])

            if best_prob < self.confidence_threshold:
                return "Other / Miscellaneous", best_prob, "Low-Confidence Fallback"

            return best_cat, round(best_prob, 3), "ML Pipeline (TF-IDF + LogReg)"

        return "Other / Miscellaneous", 0.0, "Untrained Fallback"

    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float, str]]:
        """Predicts categories for a list of narrations."""
        return [self.predict_single(t) for t in texts]

    def add_user_override(self, merchant_substring: str, category: str):
        """Allows user to override or teach the model new merchant categories."""
        if category in CATEGORIES:
            clean_key = self.preprocessor.clean_text(merchant_substring)
            self.user_overrides[clean_key] = category

    def save(self, filepath: Optional[Union[str, Path]] = None):
        """Saves trained model and overrides to disk."""
        if filepath is None:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            filepath = MODELS_DIR / "expense_classifier.joblib"

        state = {
            "pipeline": self.pipeline,
            "user_overrides": self.user_overrides,
            "confidence_threshold": self.confidence_threshold,
            "is_trained": self.is_trained
        }
        joblib.dump(state, filepath)
        print(f"[OK] Model persisted to {filepath}")

    @classmethod
    def load(cls, filepath: Optional[Union[str, Path]] = None) -> "TransactionClassifier":
        """Loads serialized model from disk."""
        if filepath is None:
            filepath = MODELS_DIR / "expense_classifier.joblib"

        state = joblib.load(filepath)
        classifier = cls(confidence_threshold=state.get("confidence_threshold", 0.35))
        classifier.pipeline = state.get("pipeline")
        classifier.user_overrides = state.get("user_overrides", {})
        classifier.is_trained = state.get("is_trained", False)
        return classifier
