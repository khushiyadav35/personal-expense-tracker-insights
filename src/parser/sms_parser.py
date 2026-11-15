"""
Regex-Based Bank & UPI SMS Extraction Pipeline
Parses unstructured SMS text notifications from major Indian banks & UPI apps.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from dateutil import parser as date_parser

from src.parser.anonymizer import TransactionAnonymizer


@dataclass
class ParsedSMS:
    """Structured representation of a parsed SMS transaction."""
    raw_text: str
    amount: float
    transaction_type: str  # 'Debit' or 'Credit'
    merchant: str
    date: str              # YYYY-MM-DD
    bank: str
    account_masked: str
    balance: Optional[float]
    reference_id: Optional[str]
    is_valid: bool


class BankSMSParser:
    """Extracts structured transactional entities from SMS strings."""

    def __init__(self):
        # Known banks and identifiers
        self.bank_identifiers = {
            "HDFC": [r"hdfc\s*bank", r"hdfc"],
            "SBI": [r"sbi", r"state\s*bank"],
            "ICICI": [r"icici\s*bank", r"icici"],
            "AXIS": [r"axis\s*bank", r"axis"],
            "KOTAK": [r"kotak\s*bank", r"kotak"],
            "PAYTM": [r"paytm"],
            "PHONEPE": [r"phonepe"],
            "GPAY": [r"google\s*pay", r"gpay"],
        }

    def detect_bank(self, text: str) -> str:
        """Identifies the originating financial institution or payment platform."""
        lower_text = text.lower()
        for bank_name, patterns in self.bank_identifiers.items():
            for pat in patterns:
                if re.search(pat, lower_text):
                    return bank_name
        return "GENERIC_BANK"

    def parse_single_sms(self, text: str) -> ParsedSMS:
        """Parses a single SMS string into a ParsedSMS object."""
        if not text or not isinstance(text, str):
            return ParsedSMS(
                raw_text="", amount=0.0, transaction_type="Debit",
                merchant="UNKNOWN", date=datetime.now().strftime("%Y-%m-%d"),
                bank="UNKNOWN", account_masked="XXXX", balance=None,
                reference_id=None, is_valid=False
            )

        clean_text = text.strip()
        lower = clean_text.lower()

        # 1. Detect Transaction Type
        if any(w in lower for w in ["credited", "received", "added to", "deposited", "cashback"]):
            tx_type = "Credit"
        elif any(w in lower for w in ["debited", "paid", "sent", "spent", "withdrawn"]):
            tx_type = "Debit"
        else:
            tx_type = "Debit"  # default fallback

        # 2. Extract Amount
        amount = 0.0
        amt_match = re.search(
            r"(?:rs\.?|inr|inr\.)\s*([\d,]+(?:\.\d{1,2})?)",
            clean_text,
            re.IGNORECASE
        )
        if amt_match:
            try:
                amount = float(amt_match.group(1).replace(",", ""))
            except ValueError:
                amount = 0.0

        # 3. Extract Account Masked
        acc_masked = "XXXX"
        acc_match = re.search(
            r"(?:a/c|acct|ac|account|ending|no\.?)\s*(?:no\.?)?\s*[\*Xx]*(\d{3,4})",
            clean_text,
            re.IGNORECASE
        )
        if acc_match:
            acc_masked = f"XX{acc_match.group(1)}"

        # 4. Extract Available / Net Balance
        balance = None
        bal_match = re.search(
            r"(?:avl\s*bal|net\s*bal|bal(?:\s*is)?:?)\s*(?:rs\.?|inr)?\s*([\d,]+(?:\.\d{1,2})?)",
            clean_text,
            re.IGNORECASE
        )
        if bal_match:
            try:
                balance = float(bal_match.group(1).replace(",", ""))
            except ValueError:
                balance = None

        # 5. Extract Reference / UTR
        reference_id = None
        ref_match = re.search(
            r"(?:ref(?:\s*no)?\.?|utr|upi\s*ref(?:[:\s]+)?)\s*([a-zA-Z0-9]{6,16})",
            clean_text,
            re.IGNORECASE
        )
        if ref_match:
            reference_id = ref_match.group(1)

        # 6. Extract Merchant
        merchant = "MISC_TRANSACTION"
        # Common patterns: "to <MERCHANT>.", "transfer to <MERCHANT>", "at <MERCHANT>.", "by UPI: <MERCHANT>."
        m_match = re.search(
            r"(?:to|transfer to|at|by upi:?|paid to|received from|by)\s+([A-Za-z0-9\s&'\.\-_]+?)(?=(?:\.|\s+ref|\s+on|\s+avl|\s+net|\s+using|\s+upi\s+ref|$))",
            clean_text,
            re.IGNORECASE
        )
        if m_match:
            candidate = m_match.group(1).strip()
            # Clean unwanted tokens from merchant
            candidate = re.sub(r"^(upi:?|vpa:?|acct|a/c)\s*", "", candidate, flags=re.IGNORECASE).strip()
            if candidate and len(candidate) > 2 and candidate.upper() not in ["A/C", "YOUR", "THE", "AN"]:
                merchant = candidate.upper()

        # 7. Extract Date
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_match = re.search(
            r"\b(\d{1,2}[-/][A-Za-z]{3,9}[-/]\d{2,4}|\d{1,2}[A-Za-z]{3}\d{2,4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b",
            clean_text
        )
        if date_match:
            try:
                parsed_dt = date_parser.parse(date_match.group(1), fuzzy=True)
                date_str = parsed_dt.strftime("%Y-%m-%d")
            except Exception:
                date_str = datetime.now().strftime("%Y-%m-%d")

        bank = self.detect_bank(clean_text)
        is_valid = amount > 0.0

        return ParsedSMS(
            raw_text=clean_text,
            amount=amount,
            transaction_type=tx_type,
            merchant=merchant,
            date=date_str,
            bank=bank,
            account_masked=acc_masked,
            balance=balance,
            reference_id=reference_id,
            is_valid=is_valid
        )

    def parse_batch_sms(self, lines: List[str]) -> List[ParsedSMS]:
        """Parses a multi-line batch of SMS alerts."""
        results = []
        for line in lines:
            line_s = line.strip()
            if line_s and not line_s.startswith("#"):
                results.append(self.parse_single_sms(line_s))
        return results
