"""
Unit Tests for Spending Forecast & What-If Simulator
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import pandas as pd
from src.forecast.forecaster import SpendingForecaster


def test_holt_linear_trend_forecasting():
    forecaster = SpendingForecaster(alpha=0.4, beta=0.2)
    # Upward linear trend
    series = [10000.0, 11000.0, 12000.0, 13000.0, 14000.0]
    pred, lower, upper = forecaster._double_exponential_smoothing(series)
    assert pred > 14000.0
    assert lower <= pred <= upper


def test_what_if_simulator():
    forecaster = SpendingForecaster()
    base_projections = [
        {"category": "Food & Dining", "projected_amount": 6000.0},
        {"category": "Shopping & E-Commerce", "projected_amount": 4000.0}
    ]
    adjustments = {"Food & Dining": -20.0, "Shopping & E-Commerce": -10.0}
    res = forecaster.simulate_what_if_scenario(base_projections, adjustments, base_income=35000.0)

    # Food cut: 20% of 6000 = 1200, Shopping cut: 10% of 4000 = 400. Total saved = 1600.
    assert res["monthly_cash_saved"] == 1600.0
    assert res["simulated_total_expense"] == 8400.0
