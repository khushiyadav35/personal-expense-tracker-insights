"""
Personal Expense Tracker with Spending Insights
Core Configuration and Taxonomy Module
Author: Khushi Yadav <ky19tech@gmail.com>
"""

from pathlib import Path
from typing import Dict, List

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
DOCS_DIR = PROJECT_ROOT / "docs"

# Standard Expense / Income Categories
CATEGORIES: List[str] = [
    "Food & Dining",
    "Groceries & Essentials",
    "Shopping & E-Commerce",
    "Transportation & Commute",
    "Bills & Utilities",
    "Entertainment & OTT",
    "Education & Books",
    "Healthcare & Medical",
    "Investments & Savings",
    "Personal Care & Services",
    "Income & Stipend",
    "Other / Miscellaneous",
]

# Color Palette for consistent visualization (Plotly / UI)
CATEGORY_COLORS: Dict[str, str] = {
    "Food & Dining": "#FF6B6B",
    "Groceries & Essentials": "#4ECDC4",
    "Shopping & E-Commerce": "#FFE66D",
    "Transportation & Commute": "#1A535C",
    "Bills & Utilities": "#F7B801",
    "Entertainment & OTT": "#9B5DE5",
    "Education & Books": "#00BBF9",
    "Healthcare & Medical": "#F15BB5",
    "Investments & Savings": "#00F5D4",
    "Personal Care & Services": "#E07A5F",
    "Income & Stipend": "#2EC4B6",
    "Other / Miscellaneous": "#ADB5BD",
}

# Monthly Default Student / Young Professional Budget (INR)
DEFAULT_MONTHLY_BUDGET: Dict[str, float] = {
    "Food & Dining": 5500.0,
    "Groceries & Essentials": 3500.0,
    "Shopping & E-Commerce": 3000.0,
    "Transportation & Commute": 2500.0,
    "Bills & Utilities": 2000.0,
    "Entertainment & OTT": 1200.0,
    "Education & Books": 1500.0,
    "Healthcare & Medical": 1000.0,
    "Investments & Savings": 3000.0,
    "Personal Care & Services": 1000.0,
    "Other / Miscellaneous": 1500.0,
}

# Alert Threshold Ratios
ALERT_THRESHOLDS = {
    "WARNING_RATIO": 0.80,    # 80% of budget consumed
    "CRITICAL_RATIO": 1.00,   # 100% of budget breached
    "SPIKE_ZSCORE": 2.20,     # Statistical anomaly threshold
}

# Known Merchant Heuristics for Zero-Shot & Rule-Based Fallback
MERCHANT_KEYWORDS: Dict[str, List[str]] = {
    "Food & Dining": [
        "swiggy", "zomato", "mcdonalds", "kfc", "dominos", "starbucks", "burger king",
        "chaayos", "chai point", "canteen", "cafe", "dhaba", "pizza", "biryani",
        "eats", "restaurant", "bakers", "sweet", "barbeque", "haldiram"
    ],
    "Groceries & Essentials": [
        "blinkit", "zepto", "instamart", "bigbasket", "dmart", "reliance fresh",
        "nature basket", "spencer", "supermarket", "kirana", "provision", "vegetables", "milk"
    ],
    "Shopping & E-Commerce": [
        "amazon", "flipkart", "myntra", "meesho", "ajio", "nykaa", "tata cliq",
        "zara", "h&m", "uniqlo", "lifestyle", "westside", "retail", "croma", "reliance digital"
    ],
    "Transportation & Commute": [
        "uber", "ola", "rapido", "irctc", "metro", "dmrc", "makemytrip", "redbus",
        "ixigo", "indianoil", "hpcl", "bpcl", "fuel", "petrol", "toll", "fastag"
    ],
    "Bills & Utilities": [
        "electricity", "airtel", "jio", "vi recharge", "bescom", "uppcl", "tneb",
        "torrent", "piped gas", "igl", "mgl", "water bill", "broadband", "act fibernet", "wifi"
    ],
    "Entertainment & OTT": [
        "netflix", "spotify", "prime video", "hotstar", "bookmyshow", "youtube",
        "playstation", "steam", "cinema", "pvr", "inox", "multiplex", "audible"
    ],
    "Education & Books": [
        "coursera", "udemy", "edx", "geeksforgeeks", "leetcode", "college fee",
        "university", "stationery", "bookstore", "kindle", "nptel", "library", "xerox"
    ],
    "Healthcare & Medical": [
        "apollo", "1mg", "pharmeasy", "netmeds", "medplus", "hospital", "clinic",
        "pathology", "diagnostic", "dr.", "dental", "opticals", "lenskart", "chemist"
    ],
    "Investments & Savings": [
        "zerodha", "groww", "kuvera", "upstox", "angel one", "mutual fund", "sip",
        "indmoney", "ppf", "nps", "fixed deposit", "recurring deposit"
    ],
    "Personal Care & Services": [
        "urban company", "salon", "spa", "parlour", "haircut", "laundry", "dry clean"
    ],
    "Income & Stipend": [
        "salary", "stipend", "interest credited", "dividend", "cashback", "refund",
        "internship", "freelance", "transfer from", "neft credit", "imps credit"
    ],
}
