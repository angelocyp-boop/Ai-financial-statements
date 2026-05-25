"""Trial balance parser: handles Excel (.xlsx, .xls) and CSV files."""
from __future__ import annotations
import os
import re
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd


_CODE_RE = re.compile(r'^[0-9]{2,8}$')


def _to_decimal(val: Any) -> Decimal:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return Decimal(0)
    try:
        return Decimal(str(val)).quantize(Decimal("0.01"))
    except InvalidOperation:
        return Decimal(0)


def _detect_columns(df: pd.DataFrame) -> dict[str, str | None]:
    """Heuristically detect which columns map to code, name, debit, credit, balance."""
    col_map: dict[str, str | None] = {
        "code": None, "name": None,
        "debit": None, "credit": None, "balance": None,
    }
    code_kws = {"code", "account code", "acc code", "account no", "account number", "no"}
    name_kws = {"name", "account name", "description", "account description", "account"}
    debit_kws = {"debit", "dr", "debits"}
    credit_kws = {"credit", "cr", "credits"}
    balance_kws = {"balance", "amount", "net", "net balance", "closing balance"}

    for col in df.columns:
        lower = str(col).lower().strip()
        if not col_map["code"] and lower in code_kws:
            col_map["code"] = col
        elif not col_map["name"] and lower in name_kws:
            col_map["name"] = col
        elif not col_map["debit"] and lower in debit_kws:
            col_map["debit"] = col
        elif not col_map["credit"] and lower in credit_kws:
            col_map["credit"] = col
        elif not col_map["balance"] and lower in balance_kws:
            col_map["balance"] = col

    # Fallback: if no name found, use first string column
    if not col_map["name"]:
        for col in df.columns:
            if df[col].dtype == object:
                col_map["name"] = col
                break

    # Fallback: if only balance (no debit/credit), that's fine
    return col_map


def parse_trial_balance(file_path: str) -> list[dict]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path, engine="openpyxl")

    # Drop entirely empty rows
    df = df.dropna(how="all")

    # Try to find the header row if file has title rows above
    for i, row in df.iterrows():
        values = [str(v).lower().strip() for v in row.values if pd.notna(v)]
        if any(v in {"debit", "credit", "balance", "dr", "cr", "amount"} for v in values):
            df.columns = df.iloc[i]
            df = df.iloc[i + 1:].reset_index(drop=True)
            df = df.dropna(how="all")
            break

    col_map = _detect_columns(df)

    if not col_map["name"]:
        raise ValueError("Could not detect account name column in trial balance")

    lines: list[dict] = []
    for _, row in df.iterrows():
        name = str(row[col_map["name"]]).strip() if col_map["name"] and pd.notna(row[col_map["name"]]) else ""
        if not name or name.lower() in {"nan", "none", "total", "grand total"}:
            continue

        code = None
        if col_map["code"] and pd.notna(row[col_map["code"]]):
            code = str(row[col_map["code"]]).strip()

        debit = _to_decimal(row[col_map["debit"]] if col_map["debit"] else None)
        credit = _to_decimal(row[col_map["credit"]] if col_map["credit"] else None)

        if col_map["balance"]:
            balance = _to_decimal(row[col_map["balance"]])
        else:
            balance = debit - credit

        lines.append({
            "account_code": code,
            "account_name": name,
            "debit": debit,
            "credit": credit,
            "balance": balance,
        })

    return lines
