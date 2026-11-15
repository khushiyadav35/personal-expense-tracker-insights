# SpendWise AI: B.Tech Capstone Project Viva Defense & Interview Guide

**Project Title:** Personal Expense Tracker with Spending Insights  
**Developer:** Khushi Yadav (Final-Year B.Tech CSE - AI & Data Science)  
**Primary Tech Stack:** Python 3.12, scikit-learn, TF-IDF NLP, Streamlit, Plotly, Pandas, GitHub Actions  

---

## 🎯 Executive Project Overview
SpendWise is an intelligent, privacy-first personal financial analytics and transaction intelligence system. It takes unstructured Indian bank SMS alerts (SBI, HDFC, ICICI, Axis, Kotak, PNB) and UPI bank statements, strips sensitive PII (account numbers, VPAs, contact details), auto-categorizes transactions using a high-precision hybrid NLP pipeline (TF-IDF + Calibrated Linear Classification), flags statistical spending anomalies (Robust Category Z-Scores & IQR), and projects next month's spending and net savings using Holt-Winters Double Exponential Smoothing.

---

## 📋 Comprehensive Viva Questions & Expert Answers

### Section A: Machine Learning & NLP Architecture

#### Q1: Why did you choose a Hybrid Architecture (Rule-based heuristics + TF-IDF with Logistic Regression) instead of an end-to-end Deep Learning model or LLM (e.g., BERT, LLaMA)?
> **Student Answer:**  
> In personal fintech, latency, explainability, and edge resource constraints are paramount:
> 1. **Ultra-Low Latency & Memory Footprint:** Financial SMS notifications arrive in real-time on mobile devices. A TF-IDF + Logistic Regression model executes in **under 2 milliseconds** with minimal RAM overhead (< 15 MB), whereas transformer models require significant GPU/CPU memory and 50–200ms latency.
> 2. **Deterministic Reliability:** Known merchant entities (such as *Swiggy*, *Uber*, *Netflix*, *Zomato*) represent over 70% of frequent transactions. Handling them via deterministic $O(1)$ token hashing guarantees **100% precision with zero hallucination**.
> 3. **High Generalization Accuracy:** For novel or noisy UPI narrations, the unigram and bigram TF-IDF representations capture merchant intent seamlessly, attaining an overall **98.48% classification accuracy** and **0.989 Macro F1-score**.

#### Q2: What is the mathematical formulation of TF-IDF used in this pipeline?
> **Student Answer:**  
> TF-IDF evaluates the relative importance of a merchant token $t$ in narration document $d$ relative to the corpus $D$:
> $$\text{TF}(t, d) = 1 + \log(f_{t,d}) \quad \text{if } f_{t,d} > 0$$
> $$\text{IDF}(t, D) = \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
> $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$
> In our implementation, we enable `sublinear_tf=True` (logarithmic scaling of term frequency) to prevent frequent repetitive tokens from dominating feature vectors.

#### Q3: Why did you implement a confidence score threshold and what happens if confidence is below 30%?
> **Student Answer:**  
> We employ a calibrated probability vector:
> $$P(y = c \mid \mathbf{x}) = \frac{e^{\mathbf{w}_c^T \mathbf{x} + b_c}}{\sum_{j} e^{\mathbf{w}_j^T \mathbf{x} + b_j}}$$
> If $\max_c P(y = c \mid \mathbf{x}) < 0.30$, the model recognizes that the narration does not exhibit strong lexical affinity to any training cluster. Instead of forcing a false-positive classification, it routes the record to `Other / Miscellaneous` and flags it for user review. Once the user assigns a category, an Active Learning override updates the local dictionary without requiring full model retraining.

---

### Section B: Privacy & Financial Data Engineering

#### Q4: How is data privacy preserved when handling user SMS messages and bank statements?
> **Student Answer:**  
> Financial privacy is enforced at the entry boundary via our `TransactionAnonymizer` engine:
> 1. **Account Number Masking:** Regex extracts only the last 4 digits (e.g., `a/c 501004281928` $\to$ `XX1928`).
> 2. **UPI VPA Scrubbing:** Usernames in handles are redacted (e.g., `khushiyadav@okaxis` $\to$ `kh***v@okaxis`).
> 3. **PII Removal:** 10-digit Indian mobile numbers (`[6-9]\d{9}`) and raw numeric transaction reference IDs are stripped before feature extraction.
> 4. **No External Network Leaks:** The analysis and parsing happen entirely within the local execution environment or client browser.

#### Q5: How do you handle heterogeneous CSV statements from different Indian banks?
> **Student Answer:**  
> Indian banks export statements in drastically different formats (e.g., HDFC uses *Withdrawal/Deposit*, SBI uses *Debit/Credit*, ICICI uses *Txn Description*). Our `StatementParser` implements a fuzzy column mapping dictionary with case-insensitive matching across known banking synonym aliases, automatically inferring dates, descriptions, transaction types, and amounts regardless of the originating institution.

---

### Section C: Statistical Anomaly Detection & Overspending Alerts

#### Q6: How does your Anomaly Detection engine differentiate between genuine spending spikes and routine variable expenses?
> **Student Answer:**  
> We implement a two-tier statistical detector:
> 1. **Category-Specific Interquartile Range (IQR):**
>    $$\text{IQR} = Q_3 - Q_1$$
>    $$\text{Upper Threshold} = Q_3 + 1.5 \times \text{IQR}$$
> 2. **Robust Z-Score Normalization:**
>    $$Z = \frac{x - \mu_{\text{category}}}{\sigma_{\text{category}}}$$
> Transactions where $Z > 2.2$ or $x > \text{Upper Threshold}$ are flagged as anomalous. By computing statistics **per category** rather than globally, high normal expenses (like rent or tuition fees) are not falsely flagged, while an unusually large grocery bill or sudden gadget shopping spree is immediately isolated.

#### Q7: What is the 3-Month Velocity Surge Alert?
> **Student Answer:**  
> It tracks category macro-trends by comparing the current month's aggregate category spend against the rolling 3-month moving average:
> $$\text{Surge Ratio} = \frac{\text{Spend}_{\text{current}}}{\frac{1}{3}\sum_{i=1}^3 \text{Spend}_{t-i}}$$
> If $\text{Surge Ratio} \ge 1.35$ (+35% increase), a velocity alert is triggered, prompting the user with an actionable recommendation to curb discretionary leakage.

---

### Section D: Time-Series Spending Forecasting

#### Q8: What algorithm did you use to forecast next month's spending and why?
> **Student Answer:**  
> We utilize **Holt's Linear Trend (Double Exponential Smoothing)**. Unlike a simple rolling average which lags behind shifts, Holt's method decomposes the expenditure time series into a baseline level ($\ell_t$) and a trend velocity ($b_t$):
> $$\ell_t = \alpha y_t + (1 - \alpha)(\ell_{t-1} + b_{t-1})$$
> $$b_t = \beta (\ell_t - \ell_{t-1}) + (1 - \beta) b_{t-1}$$
> $$\hat{y}_{t+h} = \ell_t + h \cdot b_t$$
> We tuned smoothing parameters to $\alpha = 0.4$ (smoothing of the level) and $\beta = 0.2$ (smoothing of the trend). This allows the forecast to reflect genuine upward or downward spending trends while damping out single-month noise.

#### Q9: How do you compute the 80% Confidence Interval for the forecast?
> **Student Answer:**  
> During the recursive smoothing passes, we record the historical one-step-ahead prediction residuals $e_t = y_t - \hat{y}_t$. The sample Root Mean Squared Error (RMSE) is computed:
> $$\text{RMSE} = \sqrt{\frac{1}{N}\sum_{t=1}^N (y_t - \hat{y}_t)^2}$$
> Assuming approximately Gaussian residual errors, the 80% prediction interval is calculated as:
> $$\text{CI}_{80} = \hat{y}_{t+1} \pm (1.28 \times \text{RMSE})$$

---

### Section E: Software Engineering, Testing & Deployment

#### Q10: How did you ensure test coverage across this project?
> **Student Answer:**  
> We authored a comprehensive test suite in `pytest` encompassing 12 distinct unit tests:
> - `test_sms_parser.py`: Validates regex extraction against HDFC, SBI, ICICI, and Kotak SMS notifications.
> - `test_classifier.py`: Validates rule-based lookup, ML inference, and user override active learning.
> - `test_analytics.py`: Tests cashflow calculations, 50/30/20 budget allocations, and IQR outlier detection.
> - `test_forecast.py`: Tests Holt's trend forecast equations and What-If scenario simulator arithmetic.
> Continuous Integration (CI) is automated using GitHub Actions (`.github/workflows/ci.yml`).

#### Q11: How is the application deployed publicly?
> **Student Answer:**  
> 1. **GitHub Pages Live Client App (`docs/index.html`):** Hosted directly from the repository's `/docs` directory via GitHub Pages, enabling immediate public testing of the SMS parser, charts, and simulator without requiring server infrastructure.
> 2. **Streamlit Community Cloud (`app/streamlit_app.py`):** Configured via `.streamlit/config.toml` and `requirements.txt` for one-click deployment.
> 3. **Docker Container:** Containerized with multi-stage build in `Dockerfile` and `docker-compose.yml` for self-hosted production deployment.
