"""
Unit Tests for Bank and UPI SMS Parser
Author: Khushi Yadav <ky19tech@gmail.com>
"""

import pytest
from src.parser.sms_parser import BankSMSParser


@pytest.fixture
def parser():
    return BankSMSParser()


def test_hdfc_sms_debit(parser):
    sms = "HDFC Bank: Rs 450.00 debited from a/c **4102 on 12-MAY-24 to SWIGGY. Ref 4133918231. Avl bal Rs 18,420.50"
    res = parser.parse_single_sms(sms)
    assert res.is_valid is True
    assert res.amount == 450.00
    assert res.transaction_type == "Debit"
    assert "SWIGGY" in res.merchant.upper()
    assert res.bank == "HDFC"
    assert res.account_masked == "XX4102"
    assert res.balance == 18420.50
    assert res.reference_id == "4133918231"


def test_sbi_sms_debit(parser):
    sms = "Dear SBI User, A/c 3921 debited by Rs 220.00 on 14Oct24 transfer to BLINKIT Ref No 428711092837. Avl Bal Rs 9,150.00"
    res = parser.parse_single_sms(sms)
    assert res.is_valid is True
    assert res.amount == 220.00
    assert res.transaction_type == "Debit"
    assert "BLINKIT" in res.merchant.upper()
    assert res.bank == "SBI"
    assert res.account_masked == "XX3921"


def test_credit_sms(parser):
    sms = "ICICI Bank Acct XX892 credited with INR 35,000.00 on 31-Aug-24 by INFOEDGE INTERNSHIP STIPEND. Net Bal INR 42,390.10"
    res = parser.parse_single_sms(sms)
    assert res.is_valid is True
    assert res.amount == 35000.00
    assert res.transaction_type == "Credit"
    assert res.bank == "ICICI"
    assert res.account_masked == "XX892"


def test_empty_or_invalid_sms(parser):
    res = parser.parse_single_sms("")
    assert res.is_valid is False
    assert res.amount == 0.0
