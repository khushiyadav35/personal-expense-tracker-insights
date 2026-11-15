"""
SpendWise: Personal Expense Tracker with ML Insights & Spending Forecast
Interactive Streamlit Application
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config import (
    CATEGORIES, CATEGORY_COLORS, DEFAULT_MONTHLY_BUDGET,
    PROCESSED_DATA_DIR, RAW_DATA_DIR, MODELS_DIR
)
from src.parser.sms_parser import BankSMSParser
from src.parser.statement_parser import StatementParser
from src.ml.classifier import TransactionClassifier
from src.analytics.patterns import SpendingPatternAnalyzer
from src.analytics.budget_monitor import BudgetMonitor
from src.analytics.anomaly_detector import SpendingAnomalyDetector
from src.forecast.forecaster import SpendingForecaster

# Page Configuration
st.set_page_config(
    page_title="SpendWise | Personal Expense Tracker & Insights",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        color: #F8FAFC;
    }
    .badge-safe { color: #10B981; font-weight: bold; }
    .badge-warning { color: #F59E0B; font-weight: bold; }
    .badge-critical { color: #EF4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_ml_classifier():
    """Loads or trains the hybrid ML classification engine."""
    model_path = MODELS_DIR / "expense_classifier.joblib"
    if model_path.exists():
        try:
            return TransactionClassifier.load(model_path)
        except Exception:
            pass

    # Train on processed dataset if model file not found
    dataset_path = PROCESSED_DATA_DIR / "cleaned_transactions.csv"
    classifier = TransactionClassifier(confidence_threshold=0.30)
    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        X = df["narration"].fillna(df["merchant"]).astype(str).tolist()
        y = df["category"].astype(str).tolist()
        classifier.fit(X, y)
    return classifier


@st.cache_data
def load_sample_dataset():
    """Loads the pre-curated 12-month student transaction dataset."""
    csv_path = PROCESSED_DATA_DIR / "cleaned_transactions.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return pd.DataFrame()


def main():
    classifier = load_ml_classifier()
    sms_parser = BankSMSParser()
    statement_parser = StatementParser()
    forecaster = SpendingForecaster()

    # Sidebar
    st.sidebar.title("💳 SpendWise AI")
    st.sidebar.caption("Personal Expense Tracker & Spending Insights\n**Khushi Yadav** | B.Tech CSE (AI & DS)")
    st.sidebar.markdown("---")

    # Data Source Selection
    st.sidebar.subheader("📁 Data Source")
    data_source = st.sidebar.radio(
        "Choose Transaction Feed:",
        ["Curated Indian Student Dataset (12 Months)", "Upload Custom CSV Statement", "Live SMS Input"]
    )

    df_transactions = pd.DataFrame()

    if data_source == "Curated Indian Student Dataset (12 Months)":
        df_transactions = load_sample_dataset()
        st.sidebar.success(f"✓ Loaded {len(df_transactions)} historical transactions")
    elif data_source == "Upload Custom CSV Statement":
        uploaded_file = st.sidebar.file_uploader("Upload Bank / UPI Statement CSV", type=["csv", "xlsx"])
        if uploaded_file is not None:
            df_parsed = statement_parser.parse_csv(uploaded_file)
            if not df_parsed.empty:
                # Classify transactions
                predictions = classifier.predict_batch(df_parsed["narration"].tolist())
                df_parsed["category"] = [p[0] for p in predictions]
                df_parsed["confidence"] = [p[1] for p in predictions]
                df_parsed["method"] = [p[2] for p in predictions]
                df_transactions = df_parsed
                st.sidebar.success(f"✓ Parsed & classified {len(df_transactions)} records")
            else:
                st.sidebar.error("Could not parse file. Check format.")
        else:
            st.info("👈 Please upload a bank statement CSV in the sidebar, or switch to the sample dataset.")
            df_transactions = load_sample_dataset()
    else:
        st.sidebar.info("Switch to the 'Live SMS Parser' tab to paste raw bank alerts.")
        df_transactions = load_sample_dataset()

    # Ensure Date format
    if not df_transactions.empty and "date" in df_transactions.columns:
        df_transactions["date"] = pd.to_datetime(df_transactions["date"])
        df_transactions["year_month"] = df_transactions["date"].dt.to_period("M").astype(str)

    # Main Navigation Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview & Cashflow",
        "📱 Bank SMS & UPI Parser",
        "🔍 Category Patterns & Heatmaps",
        "🚨 Overspending & Anomaly Alerts",
        "🔮 Next-Month Forecast & Simulator",
        "🎓 Architecture & Viva Defense"
    ])

    # TAB 1: OVERVIEW & CASHFLOW
    with tab1:
        st.subheader("Financial Health & Cashflow Scorecard")

        if not df_transactions.empty:
            summary = SpendingPatternAnalyzer.compute_cashflow_summary(df_transactions)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Income / Stipend", f"₹{summary['total_income']:,.2f}")
            with col2:
                st.metric("Total Expenditure", f"₹{summary['total_expense']:,.2f}")
            with col3:
                st.metric("Net Savings", f"₹{summary['net_savings']:,.2f}", delta=f"{summary['savings_rate_pct']}% rate")
            with col4:
                st.metric("Avg Transaction Size", f"₹{summary['avg_transaction_val']:,.2f}", f"{summary['transaction_count']} txns")

            st.markdown("---")

            # Monthly Cashflow Bar Chart
            col_chart1, col_chart2 = st.columns([3, 2])

            with col_chart1:
                st.markdown("##### 📈 Month-over-Month Cashflow Trend")
                monthly_trends = SpendingPatternAnalyzer.compute_monthly_trends(df_transactions)

                fig_trend = go.Figure()
                fig_trend.add_trace(go.Bar(
                    x=monthly_trends["year_month"], y=monthly_trends["Income"],
                    name="Income / Stipend", marker_color="#10B981"
                ))
                fig_trend.add_trace(go.Bar(
                    x=monthly_trends["year_month"], y=monthly_trends["Expense"],
                    name="Expenditure", marker_color="#EF4444"
                ))
                fig_trend.add_trace(go.Scatter(
                    x=monthly_trends["year_month"], y=monthly_trends["Savings"],
                    name="Net Savings", mode="lines+markers", line=dict(color="#3B82F6", width=3)
                ))
                fig_trend.update_layout(
                    barmode="group",
                    template="plotly_dark",
                    paper_bgcolor="#0F172A",
                    plot_bgcolor="#1E293B",
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_trend, use_container_width=True)

            with col_chart2:
                st.markdown("##### 🥧 Overall Expense Category Breakdown")
                cat_summary = SpendingPatternAnalyzer.compute_category_breakdown(df_transactions)

                fig_donut = px.pie(
                    cat_summary,
                    names="category",
                    values="total_amount",
                    hole=0.45,
                    color="category",
                    color_discrete_map=CATEGORY_COLORS
                )
                fig_donut.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0F172A",
                    margin=dict(l=10, r=10, t=30, b=10),
                    showlegend=False
                )
                st.plotly_chart(fig_donut, use_container_width=True)

    # TAB 2: BANK SMS & UPI PARSER
    with tab2:
        st.subheader("📱 Real-Time Bank SMS & UPI Notification Parser")
        st.markdown(
            "Paste unstructured Indian bank transaction SMS messages (HDFC, SBI, ICICI, Axis, Kotak, Paytm, PhonePe) "
            "to extract structured financial entities and classify them in real-time."
        )

        sample_sms_options = {
            "Select sample...": "",
            "HDFC Bank Swiggy Food": "HDFC Bank: Rs 420.00 debited from a/c **4102 on 12-MAY-24 to SWIGGY. Ref 4133918231. Avl bal Rs 18,420.50",
            "SBI Quick Blinkit Grocery": "Dear SBI User, A/c 3921 debited by Rs 340.00 on 14Oct24 transfer to BLINKIT Ref No 428711092837. Avl Bal Rs 9,150.00",
            "ICICI Internship Stipend Credit": "ICICI Bank Acct XX892 credited with INR 38,000.00 on 31-Aug-24 by INFOEDGE INTERNSHIP STIPEND. Net Bal INR 44,200.00",
            "Kotak Amazon Shopping": "Sent Rs.2,499.00 from Kotak Bank AC *9011 to AMAZON PAY UPI ref 4291829102. Bal: Rs.15,200.00",
            "Axis Netflix Entertainment": "Axis Bank: INR 499.00 debited from A/c no. XX5678 on 05-09-2024 at NETFLIX INDIA. UPI Ref 4248102948"
        }

        selected_sample = st.selectbox("Quick Fill Test SMS:", list(sample_sms_options.keys()))
        default_text = sample_sms_options[selected_sample] if selected_sample != "Select sample..." else ""

        user_sms_input = st.text_area("Input Bank SMS Alert Text:", value=default_text, height=100)

        if st.button("Parse & Auto-Categorize SMS", type="primary"):
            if user_sms_input.strip():
                parsed = sms_parser.parse_single_sms(user_sms_input)
                pred_cat, conf, method = classifier.predict_single(parsed.merchant)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Amount", f"₹{parsed.amount:,.2f}")
                c2.metric("Transaction Type", parsed.transaction_type)
                c3.metric("Bank Detected", parsed.bank)
                c4.metric("Account Masked", parsed.account_masked)

                st.markdown("---")
                st.markdown("##### 🧠 Machine Learning Categorization Result")

                res_c1, res_c2, res_c3 = st.columns(3)
                res_c1.info(f"**Merchant Extracted:** `{parsed.merchant}`")
                res_c2.success(f"**Predicted Category:** `{pred_cat}`")
                res_c3.metric("Model Confidence", f"{conf * 100:.1f}%", help=f"Categorized via {method}")

                with st.expander("Show JSON Extraction Details"):
                    st.json({
                        "amount": parsed.amount,
                        "transaction_type": parsed.transaction_type,
                        "merchant": parsed.merchant,
                        "category": pred_cat,
                        "confidence": conf,
                        "method": method,
                        "date": parsed.date,
                        "bank": parsed.bank,
                        "account_masked": parsed.account_masked,
                        "balance": parsed.balance,
                        "reference_id": parsed.reference_id,
                        "is_valid": parsed.is_valid
                    })
            else:
                st.warning("Please enter or select an SMS message first.")

    # TAB 3: CATEGORY INSIGHTS & HEATMAPS
    with tab3:
        st.subheader("🔍 Deep Behavioral Spending Patterns")

        if not df_transactions.empty:
            months_list = ["All Months"] + sorted(df_transactions["year_month"].unique().tolist(), reverse=True)
            chosen_month = st.selectbox("Filter Analytics by Month:", months_list)
            m_filter = None if chosen_month == "All Months" else chosen_month

            cat_df = SpendingPatternAnalyzer.compute_category_breakdown(df_transactions, month_filter=m_filter)

            col_p1, col_p2 = st.columns([3, 2])
            with col_p1:
                st.markdown("##### 📊 Category Expenditure & Transaction Velocity")
                fig_bar = px.bar(
                    cat_df,
                    x="total_amount",
                    y="category",
                    orientation="h",
                    color="category",
                    color_discrete_map=CATEGORY_COLORS,
                    text="total_amount"
                )
                fig_bar.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0F172A",
                    plot_bgcolor="#1E293B",
                    yaxis=dict(autorange="reversed"),
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_p2:
                st.markdown("##### 📅 Temporal Weekend vs Weekday Spend")
                temporal_data = SpendingPatternAnalyzer.compute_temporal_heatmaps(df_transactions)
                st.metric("Avg Weekend Daily Spend", f"₹{temporal_data['avg_weekend_ticket']:,.2f}")
                st.metric("Avg Weekday Daily Spend", f"₹{temporal_data['avg_weekday_ticket']:,.2f}")
                if temporal_data['weekend_premium_pct'] > 0:
                    st.info(f"💡 You spend **{temporal_data['weekend_premium_pct']}% more** per transaction on weekends compared to weekdays.")

            st.markdown("---")
            st.markdown("##### 🔄 Detected Recurring Subscriptions & Fixed Commitments")
            recurring = SpendingPatternAnalyzer.detect_recurring_subscriptions(df_transactions)
            if recurring:
                st.dataframe(pd.DataFrame(recurring), use_container_width=True)
            else:
                st.write("No recurring subscriptions identified.")

    # TAB 4: OVERSPENDING & ANOMALY ALERTS
    with tab4:
        st.subheader("🚨 Real-Time Overspending & Anomaly Alerts Engine")
        st.markdown(
            "Monitors category consumption against budget thresholds and uses statistical "
            "Z-scores / IQR to catch financial anomalies."
        )

        monitor = BudgetMonitor()
        detector = SpendingAnomalyDetector()

        # Monthly Budget Progress
        st.markdown("##### 🎯 Monthly Budget Threshold Tracking")
        budget_statuses = monitor.evaluate_monthly_budget(df_transactions)

        b_cols = st.columns(3)
        for idx, b in enumerate(budget_statuses[:6]):
            with b_cols[idx % 3]:
                st.markdown(f"**{b['category']}** ({b['badge']})")
                prog = min(1.0, b['spent'] / b['budgeted']) if b['budgeted'] > 0 else 0.0
                st.progress(prog)
                st.caption(f"Spent ₹{b['spent']:,.0f} of ₹{b['budgeted']:,.0f} ({b['utilization_pct']}%)")

        st.markdown("---")
        # Statistical Anomaly Detection
        st.markdown("##### ⚠️ Statistical Outlier Transactions (IQR & Z-Score Analysis)")
        outliers_df = detector.detect_transaction_outliers(df_transactions)

        if not outliers_df.empty:
            st.dataframe(
                outliers_df[["date", "narration", "category", "amount", "category_avg", "z_score", "severity", "reason"]].head(10),
                use_container_width=True
            )
        else:
            st.success("✓ No abnormal transaction spikes detected in this period.")

    # TAB 5: FORECAST & SIMULATOR
    with tab5:
        st.subheader("🔮 Next-Month Spending Forecast & What-If Simulator")
        st.markdown(
            "Projects next month's spending using Holt-Winters Double Exponential Smoothing, "
            "and simulates how behavioral changes reduce expenses."
        )

        forecast_res = forecaster.forecast_total_spending(df_transactions)
        cat_forecasts = forecaster.forecast_category_breakdown(df_transactions)

        fc1, fc2, fc3 = st.columns(3)
        fc1.metric(f"Forecasted Total Spend ({forecast_res['forecast_month']})", f"₹{forecast_res['predicted_expense']:,.2f}")
        fc2.metric("80% Confidence Range", f"₹{forecast_res['lower_bound']:,.0f} - ₹{forecast_res['upper_bound']:,.0f}")
        fc3.metric("Projected Net Savings", f"₹{forecast_res['predicted_savings']:,.2f}")

        st.markdown("---")
        st.markdown("##### 🎛️ What-If Scenario Simulator")
        st.write("Simulate adjusting your discretionary habits to see expected monthly savings:")

        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            food_cut = st.slider("Adjust Food & Dining (%):", -50, 20, -15, step=5)
            shop_cut = st.slider("Adjust Shopping & E-Commerce (%):", -50, 20, -20, step=5)
        with sim_col2:
            ent_cut = st.slider("Adjust Entertainment & OTT (%):", -50, 20, -10, step=5)
            trans_cut = st.slider("Adjust Transportation (%):", -50, 20, 0, step=5)

        adjustments = {
            "Food & Dining": food_cut,
            "Shopping & E-Commerce": shop_cut,
            "Entertainment & OTT": ent_cut,
            "Transportation & Commute": trans_cut
        }

        sim_result = forecaster.simulate_what_if_scenario(
            cat_forecasts, adjustments, base_income=forecast_res["predicted_income"]
        )

        res1, res2, res3 = st.columns(3)
        res1.metric("Simulated Monthly Spend", f"₹{sim_result['simulated_total_expense']:,.2f}", delta=f"-₹{sim_result['monthly_cash_saved']:,.2f}")
        res2.metric("Monthly Money Saved", f"₹{sim_result['monthly_cash_saved']:,.2f}", f"+{sim_result['improvement_pct']}% optimization")
        res3.metric("Annual Wealth Accumulation", f"₹{sim_result['monthly_cash_saved'] * 12:,.2f}")

    # TAB 6: ARCHITECTURE & VIVA DEFENSE
    with tab6:
        st.subheader("🎓 System Architecture & B.Tech Viva Defense Guide")
        st.markdown("""
        ### Why this Architecture?
        1. **Hybrid Classification (Rule + ML)**:
           - In real-world fintech, established merchants (Swiggy, Uber, Netflix) are known entities. A hybrid pipeline matches deterministic merchants in $O(1)$ time with 100% precision, while TF-IDF + Logistic Regression generalizes to novel merchant handles.
        2. **Explainable Anomaly Detection**:
           - Rather than treating anomaly detection as a black box, we compute category-specific Z-scores:
             $$Z = \\frac{x - \\mu}{\\sigma}$$
             and Interquartile Range ($IQR = Q_3 - Q_1$). This allows the system to articulate human-interpretable reasons for every flagged transaction.
        3. **Holt-Winters Double Exponential Smoothing**:
           - Captures baseline level ($\\ell_t$) and trend ($b_t$) without requiring hundreds of epochs of heavy neural network training, allowing sub-second inference in edge and client environments.
        """)

        st.info("💡 See `docs/VIVA_QUESTIONS_AND_ANSWERS.md` in the project root for 25+ detailed questions and answers.")


if __name__ == "__main__":
    main()
