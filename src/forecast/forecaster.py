"""
Time-Series Spending Forecasting and What-If Scenario Simulator
Implements Holt-Winters Double Exponential Smoothing and Trend Projection.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np


class SpendingForecaster:
    """Forecasts next-month expenditure and simulates budget reduction scenarios."""

    def __init__(self, alpha: float = 0.4, beta: float = 0.2):
        self.alpha = alpha  # Level smoothing parameter
        self.beta = beta    # Trend smoothing parameter

    def _double_exponential_smoothing(self, series: List[float]) -> Tuple[float, float, float]:
        """
        Holt's Linear Trend / Double Exponential Smoothing algorithm.
        Returns: (forecast_next, lower_bound_80, upper_bound_80)
        """
        n = len(series)
        if n == 0:
            return 0.0, 0.0, 0.0
        if n == 1:
            return float(series[0]), float(series[0] * 0.85), float(series[0] * 1.15)

        # Initialize level and trend
        level = series[0]
        trend = series[1] - series[0]

        residuals = []
        for i in range(1, n):
            val = series[i]
            last_level = level
            pred = level + trend
            residuals.append(val - pred)

            # Update level and trend
            level = self.alpha * val + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - last_level) + (1 - self.beta) * trend

        # 1-step-ahead forecast
        next_forecast = max(0.0, level + trend)

        # Residual Standard Error for prediction interval
        rmse = float(np.std(residuals)) if len(residuals) > 0 else (next_forecast * 0.10)
        z_80 = 1.28  # 80% confidence critical value
        margin = z_80 * rmse

        lower_bound = max(0.0, next_forecast - margin)
        upper_bound = next_forecast + margin

        return round(next_forecast, 2), round(lower_bound, 2), round(upper_bound, 2)

    def forecast_total_spending(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Forecasts next month's total expenditure and expected savings based on income trend.
        """
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        df_copy["year_month"] = df_copy["date"].dt.to_period("M").astype(str)

        monthly = df_copy.groupby(["year_month", "transaction_type"])["amount"].sum().unstack(fill_value=0.0)
        if "Debit" not in monthly.columns:
            monthly["Debit"] = 0.0
        if "Credit" not in monthly.columns:
            monthly["Credit"] = 0.0

        expense_series = monthly["Debit"].tolist()
        income_series = monthly["Credit"].tolist()
        months = monthly.index.tolist()

        if len(expense_series) < 2:
            base_val = expense_series[0] if expense_series else 15000.0
            return {
                "forecast_month": "Next Month",
                "predicted_expense": round(base_val, 2),
                "lower_bound": round(base_val * 0.85, 2),
                "upper_bound": round(base_val * 1.15, 2),
                "predicted_income": 35000.0,
                "predicted_savings": round(35000.0 - base_val, 2),
                "historical_months": months,
                "historical_expenses": expense_series
            }

        pred_exp, lower_exp, upper_exp = self._double_exponential_smoothing(expense_series)
        pred_inc, _, _ = self._double_exponential_smoothing(income_series) if any(income_series) else (38000.0, 0, 0)

        # Calculate next month name string (e.g. '2024-11')
        last_dt = pd.to_datetime(months[-1] + "-01")
        next_dt = last_dt + pd.DateOffset(months=1)
        next_month_str = next_dt.strftime("%Y-%m")

        return {
            "forecast_month": next_month_str,
            "predicted_expense": pred_exp,
            "lower_bound": lower_exp,
            "upper_bound": upper_exp,
            "predicted_income": pred_inc,
            "predicted_savings": round(pred_inc - pred_exp, 2),
            "historical_months": months,
            "historical_expenses": [round(x, 2) for x in expense_series]
        }

    def forecast_category_breakdown(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Projects next month's spending across each individual category using
        3-month weighted moving averages + trend adjustment.
        """
        df_copy = df[df["transaction_type"] == "Debit"].copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        df_copy["year_month"] = df_copy["date"].dt.to_period("M").astype(str)

        months = sorted(df_copy["year_month"].unique())
        cat_monthly = df_copy.groupby(["year_month", "category"])["amount"].sum().unstack(fill_value=0.0)

        category_projections = []
        for cat in cat_monthly.columns:
            series = cat_monthly[cat].tolist()
            pred, lower, upper = self._double_exponential_smoothing(series)
            if pred > 0:
                recent_avg = series[-1] if len(series) > 0 else pred
                trend_direction = "UP" if pred > recent_avg else "DOWN" if pred < recent_avg else "FLAT"

                category_projections.append({
                    "category": cat,
                    "projected_amount": pred,
                    "lower_bound": lower,
                    "upper_bound": upper,
                    "recent_month_actual": round(recent_avg, 2),
                    "trend": trend_direction
                })

        category_projections.sort(key=lambda x: x["projected_amount"], reverse=True)
        return category_projections

    def simulate_what_if_scenario(
        self,
        base_projections: List[Dict[str, Any]],
        category_adjustments: Dict[str, float],
        base_income: float
    ) -> Dict[str, Any]:
        """
        Simulates the financial impact of percentage reductions in specific categories.
        category_adjustments: dict of category -> percentage change (e.g. {'Food & Dining': -15.0})
        """
        adjusted_list = []
        original_total = 0.0
        new_total = 0.0

        for item in base_projections:
            cat = item["category"]
            orig_amt = item["projected_amount"]
            pct_change = category_adjustments.get(cat, 0.0)
            adj_amt = max(0.0, orig_amt * (1.0 + (pct_change / 100.0)))

            original_total += orig_amt
            new_total += adj_amt

            adjusted_list.append({
                "category": cat,
                "original_amount": round(orig_amt, 2),
                "adjusted_amount": round(adj_amt, 2),
                "percentage_change": pct_change,
                "monthly_saved": round(orig_amt - adj_amt, 2)
            })

        total_saved = original_total - new_total
        new_savings = base_income - new_total
        orig_savings = base_income - original_total

        return {
            "original_total_expense": round(original_total, 2),
            "simulated_total_expense": round(new_total, 2),
            "monthly_cash_saved": round(total_saved, 2),
            "original_savings": round(orig_savings, 2),
            "simulated_savings": round(new_savings, 2),
            "improvement_pct": round((total_saved / original_total * 100.0) if original_total > 0 else 0.0, 1),
            "category_simulations": adjusted_list
        }
