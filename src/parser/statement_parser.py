"""
Bank and UPI CSV / Excel Statement Parser
Standardizes heterogeneous statements from banks into a uniform schema.
Author: Khushi Yadav <ky19tech@gmail.com>
"""

from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
from dateutil import parser as date_parser

from src.parser.anonymizer import TransactionAnonymizer


class StatementParser:
    """Parses tabular statement exports (CSV/Excel) from banks and UPI apps."""

    # Fuzzy column name candidates for standard schema mapping
    DATE_COLS = ["date", "transaction date", "txn date", "value date", "posted date", "trans date"]
    DESC_COLS = ["narration", "description", "particulars", "remarks", "merchant", "details", "transaction details"]
    DEBIT_COLS = ["debit", "withdrawal", "dr", "debit amount", "paid out", "expense"]
    CREDIT_COLS = ["credit", "deposit", "cr", "credit amount", "paid in", "income"]
    AMOUNT_COLS = ["amount", "txn amount", "transaction amount", "net amount"]
    BALANCE_COLS = ["balance", "closing balance", "running balance", "net balance", "bal"]

    def _match_column(self, df_cols, candidates) -> Optional[str]:
        """Matches DataFrame column name against a candidate list using case-insensitive check."""
        col_map = {str(c).lower().strip(): c for c in df_cols}
        for cand in candidates:
            if cand in col_map:
                return col_map[cand]
        # Partial match
        for k, v in col_map.items():
            for cand in candidates:
                if cand in k:
                    return v
        return None

    def parse_csv(self, file_path_or_buffer) -> pd.DataFrame:
        """Parses CSV file buffer or file path into a standardized DataFrame."""
        try:
            df = pd.read_csv(file_path_or_buffer)
        except Exception:
            # Fallback for tab-separated or semicolon-separated
            df = pd.read_csv(file_path_or_buffer, sep=None, engine="python")

        if df.empty:
            return pd.DataFrame()

        # Find matching columns
        date_col = self._match_column(df.columns, self.DATE_COLS)
        desc_col = self._match_column(df.columns, self.DESC_COLS)
        debit_col = self._match_column(df.columns, self.DEBIT_COLS)
        credit_col = self._match_column(df.columns, self.CREDIT_COLS)
        amt_col = self._match_column(df.columns, self.AMOUNT_COLS)
        bal_col = self._match_column(df.columns, self.BALANCE_COLS)

        cleaned_records = []
        for idx, row in df.iterrows():
            # Date
            raw_date = row[date_col] if date_col else None
            try:
                date_val = date_parser.parse(str(raw_date), fuzzy=True).strftime("%Y-%m-%d") if raw_date else "2024-01-01"
            except Exception:
                date_val = str(raw_date)[:10]

            # Description / Narration
            raw_desc = str(row[desc_col]) if desc_col else "UNKNOWN"
            sanitized_desc = TransactionAnonymizer.sanitize_narration(raw_desc)

            # Determine Amount & Type (Debit vs Credit)
            amount = 0.0
            tx_type = "Debit"

            if debit_col and credit_col:
                raw_deb = pd.to_numeric(str(row[debit_col]).replace(",", ""), errors="coerce")
                raw_crd = pd.to_numeric(str(row[credit_col]).replace(",", ""), errors="coerce")
                if pd.notna(raw_deb) and raw_deb > 0:
                    amount = float(raw_deb)
                    tx_type = "Debit"
                elif pd.notna(raw_crd) and raw_crd > 0:
                    amount = float(raw_crd)
                    tx_type = "Credit"
                elif amt_col:
                    amount = abs(float(pd.to_numeric(str(row[amt_col]).replace(",", ""), errors="coerce") or 0.0))
            elif amt_col:
                raw_amt = pd.to_numeric(str(row[amt_col]).replace(",", ""), errors="coerce")
                if pd.notna(raw_amt):
                    amount = abs(float(raw_amt))
                    tx_type = "Credit" if raw_amt < 0 or "CR" in sanitized_desc.upper() else "Debit"

            if amount <= 0:
                continue

            balance_val = None
            if bal_col:
                raw_bal = pd.to_numeric(str(row[bal_col]).replace(",", ""), errors="coerce")
                if pd.notna(raw_bal):
                    balance_val = float(raw_bal)

            cleaned_records.append({
                "transaction_id": f"IMP_{idx+1000}",
                "date": date_val,
                "narration": sanitized_desc,
                "amount": round(amount, 2),
                "transaction_type": tx_type,
                "balance": balance_val
            })

        return pd.DataFrame(cleaned_records)
