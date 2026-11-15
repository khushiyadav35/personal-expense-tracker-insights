"""
Unit Tests for ML Transaction Classifier
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import pytest
from src.ml.classifier import TransactionClassifier


@pytest.fixture
def classifier():
    texts = [
        "swiggy bangalore upi payment",
        "zomato online food order",
        "blinkit quick grocery delivery",
        "amazon india online shopping",
        "uber india cab ride commute",
        "netflix monthly entertainment subscription",
        "airtel broadband wifi bill",
        "zerodha broking mutual fund sip",
        "apollo pharmacy medicines healthcare",
        "infoedge tech internship stipend credit"
    ]
    labels = [
        "Food & Dining",
        "Food & Dining",
        "Groceries & Essentials",
        "Shopping & E-Commerce",
        "Transportation & Commute",
        "Entertainment & OTT",
        "Bills & Utilities",
        "Investments & Savings",
        "Healthcare & Medical",
        "Income & Stipend"
    ]
    clf = TransactionClassifier(confidence_threshold=0.30)
    clf.fit(texts, labels)
    return clf


def test_rule_based_merchant(classifier):
    cat, conf, method = classifier.predict_single("SWIGGY RESTAURANT")
    assert cat == "Food & Dining"
    assert conf >= 0.95
    assert "Rule" in method


def test_ml_pipeline_generalization(classifier):
    cat, conf, method = classifier.predict_single("zomato food delivery fee")
    assert cat == "Food & Dining"
    assert conf > 0.30


def test_user_override(classifier):
    classifier.add_user_override("special bookstore", "Education & Books")
    cat, conf, method = classifier.predict_single("Payment to special bookstore lucknow")
    assert cat == "Education & Books"
    assert conf == 1.0
