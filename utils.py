import pdfplumber
import pandas as pd
import re
from datetime import datetime

def extract_metadata(lines):
    account_holder, start_date, end_date = "Unknown", None, None
    for line in lines:
        if "Account Name" in line:
            match = re.search(r'Account Name\s+(.*?)\s+Opening Balance', line)
            if match:
                account_holder = match.group(1).strip()
        elif "Electronic Account Statement From" in line:
            match = re.search(r'From (\d{2}-\d{2}-\d{4}) To (\d{2}-\d{2}-\d{4})', line)
            if match:
                start_date, end_date = match.groups()
    return account_holder, start_date, end_date

def parse_withdraw(line):
    pattern = r'^(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+(.*?)\s+([\d,]+\.\d{2})\s+-\s+([\d,]+\.\d{2})$'
    match = re.match(pattern, line.strip())
    if match:
        txn_date, value_date, desc, withdraw, balance = match.groups()
        return {
            "Txn Date": pd.to_datetime(txn_date),
            "Value Date": pd.to_datetime(value_date),
            "Description": desc.strip(),
            "Withdraw": float(withdraw.replace(',', '')),
            "Deposit": 0.0,
            "Balance": float(balance.replace(',', ''))
        }
    return None

def parse_deposit(line):
    pattern = r'^(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+(.*?)\s+-\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})$'
    match = re.match(pattern, line.strip())
    if match:
        txn_date, value_date, desc, deposit, balance = match.groups()
        return {
            "Txn Date": pd.to_datetime(txn_date),
            "Value Date": pd.to_datetime(value_date),
            "Description": desc.strip(),
            "Withdraw": 0.0,
            "Deposit": float(deposit.replace(',', '')),
            "Balance": float(balance.replace(',', ''))
        }
    return None

def parse_line(line):
    return parse_withdraw(line) or parse_deposit(line)

def extract_transactions_from_pdf(pdf_file):
    transactions = []
    account_holder, start_date, end_date = "", "", ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split("\n")
            if not account_holder:
                account_holder, start_date, end_date = extract_metadata(lines)
            for line in lines:
                txn = parse_line(line)
                if txn:
                    transactions.append(txn)
    df = pd.DataFrame(transactions)
    if not df.empty:
        df['Month'] = df['Txn Date'].dt.month
        df['Year'] = df['Txn Date'].dt.year
    return df, account_holder, start_date, end_date
