"""
Synthetic & Anonymized Indian Bank SMS & Statement Data Generator
Simulates realistic transactions for a B.Tech student / early-career engineer.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Random seed for reproducible, realistic data
random.seed(42)

# Templates for Indian Bank SMS Notifications
SMS_TEMPLATES = [
    # HDFC
    ("HDFC Bank: Rs {amount:.2f} debited from a/c **{acc} on {date_dmy} to {merchant}. Ref {ref}. Avl bal Rs {bal:.2f}", "Debit"),
    ("HDFC Bank: Rs {amount:.2f} credited to a/c **{acc} on {date_dmy} by {merchant}. Ref {ref}. Avl bal Rs {bal:.2f}", "Credit"),
    # SBI
    ("Dear SBI User, A/c {acc} debited by Rs {amount:.2f} on {date_sbi} transfer to {merchant} Ref No {ref}. Avl Bal Rs {bal:.2f}", "Debit"),
    ("Dear SBI User, your A/c ending {acc} is credited with Rs {amount:.2f} on {date_sbi} by {merchant}. Avl Bal: Rs {bal:.2f}", "Credit"),
    # ICICI
    ("ICICI Bank Acct XX{acc} debited with INR {amount:.2f} on {date_dmy} by UPI: {merchant}. Net Bal INR {bal:.2f}", "Debit"),
    ("ICICI Bank Acct XX{acc} credited with INR {amount:.2f} on {date_dmy} by {merchant}. Net Bal INR {bal:.2f}", "Credit"),
    # Kotak
    ("Sent Rs.{amount:.2f} from Kotak Bank AC *{acc} to {merchant} UPI ref {ref}. Bal: Rs.{bal:.2f}", "Debit"),
    # Axis
    ("Axis Bank: INR {amount:.2f} debited from A/c no. XX{acc} on {date_axis} at {merchant}. UPI Ref {ref}", "Debit"),
    # Paytm / UPI Apps
    ("Paid Rs.{amount:.2f} to {merchant} using UPI on Paytm. UPI Ref: {ref}", "Debit"),
    ("Money Received! Rs.{amount:.2f} received from {merchant} on PhonePe UPI. Ref: {ref}", "Credit"),
]

# Category Merchant Profiles: (Merchant Name, Typical Amount Range Min, Max, Category)
EXPENSE_PROFILES = [
    # Food & Dining
    ("SWIGGY", 180, 550, "Food & Dining"),
    ("ZOMATO", 220, 680, "Food & Dining"),
    ("DOMINOS PIZZA", 350, 850, "Food & Dining"),
    ("MCDONALDS", 180, 480, "Food & Dining"),
    ("CHAAYOS", 120, 320, "Food & Dining"),
    ("SHARMA CHAI POINT", 30, 90, "Food & Dining"),
    ("CAMPUS CAFE & CANTEEN", 60, 180, "Food & Dining"),
    ("ROYAL CAFE LUCKNOW", 450, 1200, "Food & Dining"),
    ("BURGER KING", 199, 450, "Food & Dining"),
    ("HALDIRAMS", 250, 650, "Food & Dining"),
    # Groceries & Essentials
    ("BLINKIT COMMERCE", 140, 620, "Groceries & Essentials"),
    ("ZEPTO QUICK", 160, 580, "Groceries & Essentials"),
    ("INSTAMART SWIGGY", 200, 750, "Groceries & Essentials"),
    ("BIGBASKET", 600, 1800, "Groceries & Essentials"),
    ("LOCAL KIRANA STORE", 80, 450, "Groceries & Essentials"),
    ("RELIANCE FRESH", 400, 1200, "Groceries & Essentials"),
    ("AMUL MILK DAIRY", 66, 132, "Groceries & Essentials"),
    # Shopping & E-Commerce
    ("AMAZON INDIA", 399, 2800, "Shopping & E-Commerce"),
    ("FLIPKART INTERNET", 450, 3200, "Shopping & E-Commerce"),
    ("MYNTRA DESIGNS", 799, 2999, "Shopping & E-Commerce"),
    ("AJIO ONLINE", 599, 1899, "Shopping & E-Commerce"),
    ("MEESHO PAYMENTS", 299, 899, "Shopping & E-Commerce"),
    ("ZARA RETAIL", 1990, 4500, "Shopping & E-Commerce"),
    ("CROMA ELECTRONICS", 899, 4999, "Shopping & E-Commerce"),
    # Transportation & Commute
    ("UBER INDIA RIDES", 120, 450, "Transportation & Commute"),
    ("OLA CABS", 110, 420, "Transportation & Commute"),
    ("RAPIDO BIKE TAXI", 45, 120, "Transportation & Commute"),
    ("LUCKNOW METRO RECHARGE", 200, 500, "Transportation & Commute"),
    ("IRCTC TRAIN TICKETING", 320, 1450, "Transportation & Commute"),
    ("INDIAN OIL PETROL PUMP", 200, 600, "Transportation & Commute"),
    ("FASTAG RECHARGE", 500, 1000, "Transportation & Commute"),
    # Bills & Utilities
    ("AIRTEL BROADBAND FIBER", 825, 825, "Bills & Utilities"),
    ("JIO PREPAID RECHARGE", 299, 749, "Bills & Utilities"),
    ("UPPCL ELECTRICITY BILL", 950, 2200, "Bills & Utilities"),
    ("INDRAPRASTHA GAS IGL", 480, 850, "Bills & Utilities"),
    # Entertainment & OTT
    ("NETFLIX SUBSCRIPTION", 499, 499, "Entertainment & OTT"),
    ("SPOTIFY INDIA", 119, 119, "Entertainment & OTT"),
    ("BOOKMYSHOW CINEMA", 280, 750, "Entertainment & OTT"),
    ("DISNEY HOTSTAR", 299, 899, "Entertainment & OTT"),
    ("YOUTUBE PREMIUM", 129, 129, "Entertainment & OTT"),
    ("STEAM GAMES", 499, 1800, "Entertainment & OTT"),
    # Education & Books
    ("COURSERA LEARNING", 1499, 3999, "Education & Books"),
    ("UDEMY COURSE", 449, 799, "Education & Books"),
    ("CAMPUS BOOK DEPOT", 180, 850, "Education & Books"),
    ("UNIVERSITY EXAM FEE", 1200, 2500, "Education & Books"),
    ("STATIONERY & PRINTING", 40, 220, "Education & Books"),
    # Healthcare & Medical
    ("APOLLO PHARMACY", 120, 780, "Healthcare & Medical"),
    ("TATA 1MG HEALTHCARE", 250, 1100, "Healthcare & Medical"),
    ("DR PATH LABS LUCKNOW", 600, 1500, "Healthcare & Medical"),
    ("DENTAL CARE CLINIC", 800, 2500, "Healthcare & Medical"),
    # Investments & Savings
    ("ZERODHA BROKING SIP", 2500, 5000, "Investments & Savings"),
    ("GROWW MUTUAL FUNDS", 1500, 3000, "Investments & Savings"),
    ("PPF GOVT DEPOSIT", 1000, 3000, "Investments & Savings"),
    # Personal Care & Services
    ("URBAN COMPANY SALON", 350, 950, "Personal Care & Services"),
    ("LOCAL SALON HAIRCUT", 120, 250, "Personal Care & Services"),
    ("DRY CLEAN & LAUNDRY", 150, 450, "Personal Care & Services"),
    # Miscellaneous
    ("MISCELLANEOUS UPI TRANSFER", 50, 500, "Other / Miscellaneous"),
]

INCOME_PROFILES = [
    ("STIPEND / INFOEDGE INTERNSHIP", 35000, 42000, "Income & Stipend"),
    ("FREELANCE PYTHON DEV WORK", 5000, 15000, "Income & Stipend"),
    ("SAVINGS BANK INTEREST CREDITED", 180, 450, "Income & Stipend"),
    ("REFUND FROM ECOMMERCE", 250, 1850, "Income & Stipend"),
    ("FAMILY POCKET SUPPORT", 4000, 8000, "Income & Stipend"),
]

BANKS = ["HDFC", "SBI", "ICICI", "KOTAK", "AXIS"]
PAYMENT_MODES = ["UPI", "UPI", "UPI", "Debit Card", "Net Banking", "IMPS"]


def generate_dataset(num_days=365):
    """Generate 12-month synthetic transaction log and SMS alerts."""
    start_date = datetime(2023, 11, 1)
    current_balance = 28500.0

    transactions = []
    sms_lines = []
    tx_counter = 10001

    for day_offset in range(num_days):
        current_day = start_date + timedelta(days=day_offset)
        day_str_dmy = current_day.strftime("%d-%b-%y").upper()
        day_str_sbi = current_day.strftime("%d%b%y")
        day_str_axis = current_day.strftime("%d-%m-%Y")
        iso_date = current_day.strftime("%Y-%m-%d")

        # Monthly Stipend credit around day 28-31
        if current_day.day in [28, 29, 30] and random.random() < 0.35:
            # Check if this month already had a stipend
            month_key = current_day.strftime("%Y-%m")
            stipend_given = any(t['date'].startswith(month_key) and "INTERNSHIP" in t['narration'] for t in transactions)
            if not stipend_given:
                amount = round(random.uniform(35000, 42000), 2)
                current_balance += amount
                ref_num = f"{random.randint(400000000000, 499999999999)}"
                acc_num = f"{random.randint(1000, 9999)}"
                bank = "HDFC"
                tx_desc = "NEFT CR-INFOEDGE TECH-INTERNSHIP STIPEND"
                cat = "Income & Stipend"

                transactions.append({
                    "transaction_id": f"TXN_{tx_counter}",
                    "date": iso_date,
                    "time": "11:20:00",
                    "narration": tx_desc,
                    "merchant": "INFOEDGE TECH",
                    "amount": amount,
                    "transaction_type": "Credit",
                    "category": cat,
                    "payment_mode": "NEFT",
                    "bank": bank,
                    "account_masked": f"XX{acc_num}",
                    "balance": round(current_balance, 2),
                    "is_anomaly": False
                })
                tx_counter += 1

                # Add SMS
                sms_lines.append(f"HDFC Bank: Rs {amount:.2f} credited to a/c **{acc_num} on {day_str_dmy} by INFOEDGE TECH STIPEND. Ref {ref_num}. Avl bal Rs {current_balance:.2f}")

        # Monthly Fixed Subscriptions / Rent on 1st - 5th
        if current_day.day in [1, 2, 3, 4, 5]:
            month_key = current_day.strftime("%Y-%m")
            rent_paid = any(t['date'].startswith(month_key) and "HOSTEL" in t['narration'] for t in transactions)
            if not rent_paid and current_day.day == 2:
                # PG / Hostel Rent
                rent_amt = 8500.0
                current_balance -= rent_amt
                ref_num = f"{random.randint(400000000000, 499999999999)}"
                acc_num = f"{random.randint(1000, 9999)}"
                transactions.append({
                    "transaction_id": f"TXN_{tx_counter}",
                    "date": iso_date,
                    "time": "09:30:00",
                    "narration": "UPI/HOSTEL RENT PG ACCOMMODATION/LUCKNOW",
                    "merchant": "HOSTEL RENT PG",
                    "amount": rent_amt,
                    "transaction_type": "Debit",
                    "category": "Bills & Utilities",
                    "payment_mode": "UPI",
                    "bank": "HDFC",
                    "account_masked": f"XX{acc_num}",
                    "balance": round(current_balance, 2),
                    "is_anomaly": False
                })
                tx_counter += 1
                sms_lines.append(f"HDFC Bank: Rs {rent_amt:.2f} debited from a/c **{acc_num} on {day_str_dmy} to HOSTEL RENT PG. Ref {ref_num}. Avl bal Rs {current_balance:.2f}")

            # SIP Investment on 5th
            sip_done = any(t['date'].startswith(month_key) and "ZERODHA" in t['narration'] for t in transactions)
            if not sip_done and current_day.day == 5:
                sip_amt = 3000.0
                current_balance -= sip_amt
                ref_num = f"{random.randint(400000000000, 499999999999)}"
                acc_num = f"{random.randint(1000, 9999)}"
                transactions.append({
                    "transaction_id": f"TXN_{tx_counter}",
                    "date": iso_date,
                    "time": "08:00:00",
                    "narration": "NACH/ZERODHA BROKING MUTUAL FUND SIP",
                    "merchant": "ZERODHA BROKING",
                    "amount": sip_amt,
                    "transaction_type": "Debit",
                    "category": "Investments & Savings",
                    "payment_mode": "Net Banking",
                    "bank": "HDFC",
                    "account_masked": f"XX{acc_num}",
                    "balance": round(current_balance, 2),
                    "is_anomaly": False
                })
                tx_counter += 1
                sms_lines.append(f"HDFC Bank: Rs {sip_amt:.2f} debited from a/c **{acc_num} on {day_str_dmy} to ZERODHA BROKING. Ref {ref_num}. Avl bal Rs {current_balance:.2f}")

        # Daily Variable Expenses (1 to 5 transactions per day)
        num_daily_tx = random.choices([1, 2, 3, 4, 5], weights=[0.25, 0.35, 0.25, 0.10, 0.05])[0]

        # Festival / Anomaly event in October (Diwali) or July (Medical)
        is_diwali_sale = (current_day.month == 10 and 15 <= current_day.day <= 25)
        is_medical_event = (current_day.month == 7 and current_day.day == 14)

        for _ in range(num_daily_tx):
            if is_medical_event and random.random() < 0.4:
                merchant, min_a, max_a, cat = ("DENTAL CARE & ORTHO CLINIC", 4200, 4800, "Healthcare & Medical")
                is_anomaly = True
            elif is_diwali_sale and random.random() < 0.3:
                merchant, min_a, max_a, cat = random.choice([
                    ("AMAZON INDIA DIWALI SALE", 4500, 9500, "Shopping & E-Commerce"),
                    ("MYNTRA FESTIVE SHOPPING", 3200, 6800, "Shopping & E-Commerce")
                ])
                is_anomaly = True
            else:
                merchant, min_a, max_a, cat = random.choice(EXPENSE_PROFILES)
                is_anomaly = False

            amount = round(random.uniform(min_a, max_a), 2)
            current_balance -= amount
            if current_balance < 1500:
                # Add a family support transfer if balance is low
                refill = 5000.0
                current_balance += refill
                transactions.append({
                    "transaction_id": f"TXN_{tx_counter}",
                    "date": iso_date,
                    "time": "14:15:00",
                    "narration": "UPI/TRANSFER FROM FAMILY POCKET SUPPORT",
                    "merchant": "FAMILY POCKET SUPPORT",
                    "amount": refill,
                    "transaction_type": "Credit",
                    "category": "Income & Stipend",
                    "payment_mode": "UPI",
                    "bank": "SBI",
                    "account_masked": "XX4821",
                    "balance": round(current_balance, 2),
                    "is_anomaly": False
                })
                tx_counter += 1

            hour = random.randint(8, 23)
            minute = random.randint(0, 59)
            time_str = f"{hour:02d}:{minute:02d}:00"
            bank = random.choice(BANKS)
            acc_num = f"{random.randint(1000, 9999)}"
            ref_num = f"{random.randint(400000000000, 499999999999)}"
            mode = random.choice(PAYMENT_MODES)

            narration = f"UPI/{merchant}/{ref_num[:6]}/{mode}"

            transactions.append({
                "transaction_id": f"TXN_{tx_counter}",
                "date": iso_date,
                "time": time_str,
                "narration": narration,
                "merchant": merchant,
                "amount": amount,
                "transaction_type": "Debit",
                "category": cat,
                "payment_mode": mode,
                "bank": bank,
                "account_masked": f"XX{acc_num}",
                "balance": round(current_balance, 2),
                "is_anomaly": is_anomaly
            })
            tx_counter += 1

            # Generate SMS representation for ~40% of transactions to build realistic SMS corpus
            if random.random() < 0.40:
                if bank == "HDFC":
                    sms = f"HDFC Bank: Rs {amount:.2f} debited from a/c **{acc_num} on {day_str_dmy} to {merchant}. Ref {ref_num}. Avl bal Rs {current_balance:.2f}"
                elif bank == "SBI":
                    sms = f"Dear SBI User, A/c {acc_num} debited by Rs {amount:.2f} on {day_str_sbi} transfer to {merchant} Ref No {ref_num}. Avl Bal Rs {current_balance:.2f}"
                elif bank == "ICICI":
                    sms = f"ICICI Bank Acct XX{acc_num} debited with INR {amount:.2f} on {day_str_dmy} by UPI: {merchant}. Net Bal INR {current_balance:.2f}"
                elif bank == "KOTAK":
                    sms = f"Sent Rs.{amount:.2f} from Kotak Bank AC *{acc_num} to {merchant} UPI ref {ref_num}. Bal: Rs.{current_balance:.2f}"
                else:
                    sms = f"Axis Bank: INR {amount:.2f} debited from A/c no. XX{acc_num} on {day_str_axis} at {merchant}. UPI Ref {ref_num}"
                sms_lines.append(sms)

    # Save to CSV files
    csv_file = RAW_DIR / "upi_statement_sample.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(transactions[0].keys()))
        writer.writeheader()
        writer.writerows(transactions)

    # Save processed copy
    processed_csv = PROCESSED_DIR / "cleaned_transactions.csv"
    with open(processed_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(transactions[0].keys()))
        writer.writeheader()
        writer.writerows(transactions)

    # Save Raw Bank SMS Corpus
    sms_file = RAW_DIR / "bank_sms_raw.txt"
    with open(sms_file, mode="w", encoding="utf-8") as f:
        f.write("\n".join(sms_lines))

    print(f"[OK] Generated {len(transactions)} transactions in {csv_file}")
    print(f"[OK] Generated {len(sms_lines)} realistic bank SMS alerts in {sms_file}")


if __name__ == "__main__":
    generate_dataset(num_days=365)
