"""
Dynamic Budget Monitoring and Threshold Breach Engine
Tracks category expenditure against budget goals and 50/30/20 guidelines.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from src.config import DEFAULT_MONTHLY_BUDGET, ALERT_THRESHOLDS


class BudgetMonitor:
    """Manages monthly category budgets, consumption tracking, and alert triggers."""

    def __init__(self, custom_budget: Optional[Dict[str, float]] = None):
        self.budgets = custom_budget or DEFAULT_MONTHLY_BUDGET.copy()
        self.warning_ratio = ALERT_THRESHOLDS["WARNING_RATIO"]
        self.critical_ratio = ALERT_THRESHOLDS["CRITICAL_RATIO"]

    def set_category_budget(self, category: str, amount: float):
        """Updates or sets budget for a specific category."""
        if amount >= 0:
            self.budgets[category] = float(amount)

    def evaluate_monthly_budget(self, df: pd.DataFrame, target_month: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Evaluates category spending against budgeted allocations for target_month (YYYY-MM).
        Returns a list of budget status dicts with consumption ratio and alert level.
        """
        df_copy = df[df["transaction_type"] == "Debit"].copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])

        if target_month:
            df_copy = df_copy[df_copy["date"].dt.to_period("M").astype(str) == target_month]
        elif not df_copy.empty:
            # Default to most recent month
            target_month = df_copy["date"].dt.to_period("M").astype(str).max()
            df_copy = df_copy[df_copy["date"].dt.to_period("M").astype(str) == target_month]

        actual_spend = df_copy.groupby("category")["amount"].sum().to_dict()

        results = []
        for cat, budgeted in self.budgets.items():
            spent = actual_spend.get(cat, 0.0)
            ratio = spent / budgeted if budgeted > 0 else 0.0
            remaining = budgeted - spent

            if ratio >= self.critical_ratio:
                status = "CRITICAL_OVERSPEND"
                alert_badge = "🔴 Over Budget"
                color = "#EF4444"
            elif ratio >= self.warning_ratio:
                status = "WARNING"
                alert_badge = "🟡 Approaching Limit"
                color = "#F59E0B"
            else:
                status = "ON_TRACK"
                alert_badge = "🟢 Safe"
                color = "#10B981"

            results.append({
                "month": target_month,
                "category": cat,
                "budgeted": round(budgeted, 2),
                "spent": round(spent, 2),
                "remaining": round(remaining, 2),
                "utilization_pct": round(ratio * 100.0, 1),
                "status": status,
                "badge": alert_badge,
                "color": color
            })

        results.sort(key=lambda x: x["utilization_pct"], reverse=True)
        return results

    def compute_50_30_20_allocation(self, total_income: float) -> Dict[str, Any]:
        """Calculates classic 50/30/20 rule allocation based on monthly net income."""
        needs = total_income * 0.50
        wants = total_income * 0.30
        savings = total_income * 0.20
        return {
            "needs_allocated": round(needs, 2),
            "wants_allocated": round(wants, 2),
            "savings_allocated": round(savings, 2)
        }
