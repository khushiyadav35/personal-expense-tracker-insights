"""
Statistical Spending Anomaly and Outlier Detection Engine
Employs Robust Z-Scores and Interquartile Range (IQR) for automated alert generation.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class SpendingAnomalyDetector:
    """Detects unusual single transactions and macro monthly spending spikes."""

    def __init__(self, zscore_threshold: float = 2.2, iqr_multiplier: float = 1.5):
        self.zscore_threshold = zscore_threshold
        self.iqr_multiplier = iqr_multiplier

    def detect_transaction_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Flags individual transactions that deviate significantly from category norms
        using category-specific IQR and Z-scores.
        """
        expense_df = df[df["transaction_type"] == "Debit"].copy()
        if expense_df.empty:
            return pd.DataFrame()

        outliers = []
        for cat, group in expense_df.groupby("category"):
            if len(group) < 4:
                continue

            amounts = group["amount"]
            mean_val = amounts.mean()
            std_val = amounts.std()

            q25 = amounts.quantile(0.25)
            q75 = amounts.quantile(0.75)
            iqr = q75 - q25
            upper_iqr = q75 + (self.iqr_multiplier * iqr)

            for idx, row in group.iterrows():
                amt = row["amount"]
                zscore = (amt - mean_val) / std_val if std_val > 0 else 0.0

                is_iqr_outlier = amt > upper_iqr
                is_zscore_outlier = zscore > self.zscore_threshold

                if is_iqr_outlier or is_zscore_outlier:
                    outliers.append({
                        "transaction_id": row.get("transaction_id", f"TXN_{idx}"),
                        "date": str(row["date"])[:10],
                        "narration": row.get("narration", row.get("merchant", "Expense")),
                        "category": cat,
                        "amount": round(float(amt), 2),
                        "category_avg": round(float(mean_val), 2),
                        "z_score": round(float(zscore), 2),
                        "deviation_pct": round(((amt - mean_val) / mean_val * 100.0) if mean_val > 0 else 0.0, 1),
                        "severity": "HIGH" if zscore > 3.0 or amt > (upper_iqr * 1.5) else "MODERATE",
                        "reason": f"Amount Rs.{amt:.2f} is {((amt - mean_val) / mean_val * 100.0):.0f}% higher than typical {cat} average (Rs.{mean_val:.2f})"
                    })

        outliers_df = pd.DataFrame(outliers)
        if not outliers_df.empty:
            return outliers_df.sort_values(by="amount", ascending=False)
        return pd.DataFrame()

    def detect_monthly_category_surges(self, df: pd.DataFrame, surge_ratio: float = 1.35) -> List[Dict[str, Any]]:
        """
        Detects if a category's current month expenditure surges by more than
        surge_ratio (e.g. 35%) over the rolling 3-month baseline average.
        """
        df_copy = df[df["transaction_type"] == "Debit"].copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        df_copy["year_month"] = df_copy["date"].dt.to_period("M").astype(str)

        months = sorted(df_copy["year_month"].unique())
        if len(months) < 2:
            return []

        latest_month = months[-1]
        past_months = months[-4:-1] if len(months) >= 4 else months[:-1]

        latest_data = df_copy[df_copy["year_month"] == latest_month]
        past_data = df_copy[df_copy["year_month"].isin(past_months)]

        latest_cat_sum = latest_data.groupby("category")["amount"].sum()
        past_cat_mean = past_data.groupby(["year_month", "category"])["amount"].sum().groupby("category").mean()

        alerts = []
        for cat, current_val in latest_cat_sum.items():
            baseline_val = past_cat_mean.get(cat, 0.0)
            if baseline_val > 500:  # ignore trivial categories
                ratio = current_val / baseline_val
                if ratio >= surge_ratio:
                    surge_pct = (ratio - 1.0) * 100.0
                    alerts.append({
                        "month": latest_month,
                        "category": cat,
                        "current_spending": round(float(current_val), 2),
                        "historical_baseline": round(float(baseline_val), 2),
                        "surge_pct": round(surge_pct, 1),
                        "severity": "CRITICAL" if surge_pct > 60 else "WARNING",
                        "message": f"Spending in '{cat}' surged by {surge_pct:.1f}% compared to your past 3-month average."
                    })

        alerts.sort(key=lambda x: x["surge_pct"], reverse=True)
        return alerts
