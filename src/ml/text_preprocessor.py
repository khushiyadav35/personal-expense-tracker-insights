"""
Financial Text Preprocessing and Token Cleaning
Cleans raw bank narration strings for ML feature extraction.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import re
from typing import List


class TransactionTextPreprocessor:
    """Cleans and standardizes raw bank narrations and merchant strings."""

    FINANCIAL_STOPWORDS = {
        "rs", "inr", "upi", "imps", "neft", "rtgs", "cr", "dr", "debit", "debited",
        "credit", "credited", "ac", "acct", "a/c", "account", "no", "ref", "utr",
        "tx", "txn", "transaction", "transfer", "to", "from", "at", "by", "via",
        "using", "avl", "bal", "balance", "net", "ending", "bank", "ltd", "pvt",
        "corp", "co", "card", "payment", "paid", "sent", "received", "money"
    }

    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Normalizes and strips transactional noise from narration text.
        Example: 'UPI/SWIGGY/413391/UPI' -> 'swiggy'
                 'POS 429101 AMAZON INDIA BANGALORE' -> 'amazon india'
        """
        if not text or not isinstance(text, str):
            return ""

        # Lowercase
        cleaned = text.lower()

        # Replace slash, hyphens, underscores with spaces
        cleaned = re.sub(r"[\/\-_\\\|:@#*]", " ", cleaned)

        # Remove numbers and reference codes (e.g. 4289192, xx1234)
        cleaned = re.sub(r"\b\d+\b", " ", cleaned)
        cleaned = re.sub(r"\bxx\d+\b", " ", cleaned)

        # Remove punctuation
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)

        # Tokenize and remove financial stopwords and short single-character tokens
        tokens = [
            token.strip()
            for token in cleaned.split()
            if len(token.strip()) > 1 and token.strip() not in cls.FINANCIAL_STOPWORDS
        ]

        return " ".join(tokens)

    @classmethod
    def clean_batch(cls, texts: List[str]) -> List[str]:
        """Preprocesses a list of narration strings."""
        return [cls.clean_text(t) for t in texts]
