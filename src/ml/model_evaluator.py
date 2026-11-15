"""
Model Performance Evaluation and Metrics Reporting
Calculates Precision, Recall, F1-Score, and Confusion Matrix.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

from typing import Dict, Any, List
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


class ModelEvaluator:
    """Evaluates multi-class transaction classification models."""

    @staticmethod
    def evaluate(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
        """Computes comprehensive evaluation metrics."""
        unique_labels = sorted(list(set(y_true) | set(y_pred)))
        acc = accuracy_score(y_true, y_pred)
        report_dict = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        report_text = classification_report(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=unique_labels)

        cm_df = pd.DataFrame(cm, index=unique_labels, columns=unique_labels)

        return {
            "accuracy": round(acc, 4),
            "macro_f1": round(report_dict["macro avg"]["f1-score"], 4),
            "weighted_f1": round(report_dict["weighted avg"]["f1-score"], 4),
            "classification_report_dict": report_dict,
            "classification_report_text": report_text,
            "confusion_matrix_df": cm_df,
            "labels": unique_labels
        }
