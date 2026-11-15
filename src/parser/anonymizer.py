"""
Privacy-Preserving Anonymization Engine for Financial Records
Masks PII, bank account numbers, UPI handles, and sensitive reference keys.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import re
from typing import Optional


class TransactionAnonymizer:
    """Provides methods to sanitize sensitive personal financial identifiers."""

    @staticmethod
    def mask_account_number(account_str: str) -> str:
        """
        Masks bank account numbers to show only the last 3-4 digits.
        Example: '501004281928' -> 'XXXX-XXXX-1928'
        """
        if not account_str:
            return "XXXX"
        digits = re.findall(r"\d", str(account_str))
        if len(digits) >= 4:
            return f"XX{''.join(digits[-4:])}"
        return "XX****"

    @staticmethod
    def mask_upi_handle(vpa: str) -> str:
        """
        Masks UPI Virtual Payment Address (VPA).
        Example: 'khushiyadav@okaxis' -> 'kh***v@okaxis'
        """
        if not vpa or "@" not in str(vpa):
            return str(vpa)
        parts = vpa.split("@")
        username = parts[0]
        domain = parts[1] if len(parts) > 1 else "upi"

        if len(username) <= 2:
            masked_user = f"{username[0]}*"
        elif len(username) <= 4:
            masked_user = f"{username[0]}**{username[-1]}"
        else:
            masked_user = f"{username[:2]}***{username[-2:]}"

        return f"{masked_user}@{domain}"

    @staticmethod
    def mask_phone_number(text: str) -> str:
        """Masks 10-digit Indian mobile numbers found in text."""
        return re.sub(r"(?:\+91[\-\s]?)?[6-9]\d{9}", "[PHONE_MASKED]", text)

    @staticmethod
    def sanitize_narration(narration: str) -> str:
        """
        Removes sensitive personal names, phone numbers, and raw numeric reference strings
        while preserving the underlying merchant and payment channel context.
        """
        if not narration:
            return ""
        # Remove phone numbers
        text = re.sub(r"(?:\+91[\-\s]?)?[6-9]\d{9}", "", narration)
        # Mask long reference / UTR numbers (8-16 digits)
        text = re.sub(r"\b\d{8,16}\b", "[REF]", text)
        # Normalize multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text
