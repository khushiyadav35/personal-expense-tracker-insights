"""
Unit Tests for Analytics, Budget Monitoring, and Anomaly Detection
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import pandas as pd
from src.analytics.patterns import SpendingPatternAnalyzer
from src.analytics.budget_monitor import BudgetMonitor
from src.analytics.anomaly_detector import SpendingAnomalyDetector


def test_cashflow_summary():
    df = pd.DataFrame([
        {"transaction_type": "Credit", "amount": 40000.0},
        {"transaction_type": "Debit", "amount": 15000.0},
        {"transaction_type": "Debit", "amount": 5000.0},
    ])
    summary = SpendingPatternAnalyzer.compute_cashflow_summary(df)
    assert summary["total_income"] == 40000.0
    assert summary["total_expense"] == 20000.0
    assert summary["net_savings"] == 20000.0
    assert summary["savings_rate_pct"] == 50.0


def test_budget_monitor_eval():
    monitor = BudgetMonitor({"Food & Dining": 5000.0})
    df = pd.DataFrame([
        {"date": "2024-05-10", "category": "Food & Dining", "amount": 6000.0, "transaction_type": "Debit"}
    ])
    statuses = monitor.evaluate_monthly_budget(df, target_month="2024-05")
    food_status = next(s for s in statuses if s["category"] == "Food & Dining")
    assert food_status["status"] == "CRITICAL_OVERSPEND"
    assert food_status["utilization_pct"] == 120.0


def test_anomaly_detection_outlier():
    detector = SpendingAnomalyDetector(zscore_threshold=2.0)
    data = [
        {"date": "2024-01-01", "narration": "swiggy", "category": "Food & Dining", "amount": 200.0, "transaction_type": "Debit"},
        {"date": "2024-01-02", "narration": "swiggy", "category": "Food & Dining", "amount": 250.0, "transaction_type": "Debit"},
        {"date": "2024-01-03", "narration": "swiggy", "category": "Food & Dining", "amount": 220.0, "transaction_type": "Debit"},
        {"date": "2024-01-04", "narration": "swiggy", "category": "Food & Dining", "amount": 210.0, "transaction_type": "Debit"},
        {"date": "2024-01-05", "narration": "swiggy mega feast", "category": "Food & Dining", "amount": 4500.0, "transaction_type": "Debit"},
    ]
    df = pd.DataFrame(data)
    outliers = detector.detect_transaction_outliers(df)
    assert not outliers.empty
    assert outliers.iloc[0]["amount"] == 4500.0
