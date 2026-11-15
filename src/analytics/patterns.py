"""
Spending Pattern Analysis and Recurring Transaction Detector
Extracts behavioral spending trends, temporal patterns, and recurring bills.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class SpendingPatternAnalyzer:
    """Computes monthly patterns, cash flow metrics, and behavioral insights."""

    @staticmethod
    def compute_cashflow_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates total income, total expenditure, net savings, and savings rate."""
        if df.empty:
            return {"total_income": 0.0, "total_expense": 0.0, "net_savings": 0.0, "savings_rate_pct": 0.0}

        income_df = df[df["transaction_type"] == "Credit"]
        expense_df = df[df["transaction_type"] == "Debit"]

        total_income = float(income_df["amount"].sum())
        total_expense = float(expense_df["amount"].sum())
        net_savings = total_income - total_expense
        savings_rate = (net_savings / total_income * 100.0) if total_income > 0 else 0.0

        return {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate_pct": round(savings_rate, 2),
            "transaction_count": len(df),
            "avg_transaction_val": round(float(expense_df["amount"].mean()) if not expense_df.empty else 0.0, 2)
        }

    @staticmethod
    def compute_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
        """Groups transactions by Year-Month and computes monthly income, expense, and savings."""
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        df_copy["year_month"] = df_copy["date"].dt.to_period("M").astype(str)

        grouped = df_copy.groupby(["year_month", "transaction_type"])["amount"].sum().unstack(fill_value=0.0)

        if "Credit" not in grouped.columns:
            grouped["Credit"] = 0.0
        if "Debit" not in grouped.columns:
            grouped["Debit"] = 0.0

        grouped["Income"] = grouped["Credit"]
        grouped["Expense"] = grouped["Debit"]
        grouped["Savings"] = grouped["Income"] - grouped["Expense"]
        grouped["Savings_Rate"] = np.where(grouped["Income"] > 0, (grouped["Savings"] / grouped["Income"]) * 100, 0.0)

        return grouped[["Income", "Expense", "Savings", "Savings_Rate"]].reset_index()

    @staticmethod
    def compute_category_breakdown(df: pd.DataFrame, month_filter: Optional[str] = None) -> pd.DataFrame:
        """Computes spending per category, percentage share, and transaction frequency."""
        df_copy = df[df["transaction_type"] == "Debit"].copy()
        if month_filter:
            df_copy["date"] = pd.to_datetime(df_copy["date"])
            df_copy = df_copy[df_copy["date"].dt.to_period("M").astype(str) == month_filter]

        if df_copy.empty:
            return pd.DataFrame(columns=["category", "total_amount", "percentage", "count", "avg_per_tx"])

        cat_grouped = df_copy.groupby("category").agg(
            total_amount=("amount", "sum"),
            count=("amount", "count"),
            avg_per_tx=("amount", "mean")
        ).reset_index()

        total_spend = cat_grouped["total_amount"].sum()
        cat_grouped["percentage"] = (cat_grouped["total_amount"] / total_spend * 100.0).round(2)
        cat_grouped["total_amount"] = cat_grouped["total_amount"].round(2)
        cat_grouped["avg_per_tx"] = cat_grouped["avg_per_tx"].round(2)

        return cat_grouped.sort_values(by="total_amount", ascending=False)

    @staticmethod
    def compute_temporal_heatmaps(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates day-of-week and weekend vs weekday spending patterns."""
        df_copy = df[df["transaction_type"] == "Debit"].copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        df_copy["day_name"] = df_copy["date"].dt.day_name()
        df_copy["is_weekend"] = df_copy["date"].dt.weekday >= 5

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_spend = df_copy.groupby("day_name")["amount"].agg(["sum", "mean", "count"]).reindex(day_order).fillna(0.0)

        weekend_spend = df_copy[df_copy["is_weekend"]]["amount"].mean()
        weekday_spend = df_copy[~df_copy["is_weekend"]]["amount"].mean()

        return {
            "day_of_week_df": day_spend.reset_index(),
            "avg_weekend_ticket": round(float(weekend_spend) if not np.isnan(weekend_spend) else 0.0, 2),
            "avg_weekday_ticket": round(float(weekday_spend) if not np.isnan(weekday_spend) else 0.0, 2),
            "weekend_premium_pct": round(((weekend_spend - weekday_spend) / weekday_spend * 100.0) if weekday_spend > 0 else 0.0, 2)
        }

    @staticmethod
    def detect_recurring_subscriptions(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detects recurring monthly subscriptions, rents, utilities, and SIPs
        by checking frequency (>= 3 occurrences) and low amount variance.
        """
        expense_df = df[df["transaction_type"] == "Debit"].copy()
        if "merchant" not in expense_df.columns:
            expense_df["merchant"] = expense_df["narration"]

        recurring_items = []
        for merchant, group in expense_df.groupby("merchant"):
            if len(group) >= 3:
                amt_std = group["amount"].std()
                amt_mean = group["amount"].mean()
                cv = (amt_std / amt_mean) if amt_mean > 0 else 1.0  # Coefficient of Variation

                # If standard deviation is low relative to mean (< 15%), it's likely a recurring subscription
                if cv < 0.15 or (len(group) >= 4 and cv < 0.25):
                    recurring_items.append({
                        "merchant": merchant,
                        "category": group["category"].iloc[0] if "category" in group else "Recurring",
                        "frequency": len(group),
                        "avg_amount": round(float(amt_mean), 2),
                        "total_spent": round(float(group["amount"].sum()), 2),
                        "projected_annual_cost": round(float(amt_mean * 12), 2)
                    })

        recurring_items.sort(key=lambda x: x["avg_amount"], reverse=True)
        return recurring_items
