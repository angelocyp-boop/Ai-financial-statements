"""Validation engine - runs all checks on a financial engagement."""
from __future__ import annotations
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.validation import ValidationResult, ValidationSeverity
from app.models.trial_balance import TrialBalance, TBLine
from app.models.statement import FinancialStatement
from app.models.engagement import Engagement


def _clear_existing(eng_id: int, db: Session) -> None:
    db.query(ValidationResult).filter(
        ValidationResult.engagement_id == eng_id,
        ValidationResult.is_resolved == False,
    ).delete()
    db.flush()


def _add_result(eng_id: int, check_type: str, severity: ValidationSeverity, message: str, details: str, db: Session) -> None:
    db.add(ValidationResult(
        engagement_id=eng_id,
        check_type=check_type,
        severity=severity,
        message=message,
        details=details,
    ))


def check_balance_sheet_equation(eng_id: int, db: Session) -> None:
    stmts = db.query(FinancialStatement).filter(
        FinancialStatement.engagement_id == eng_id,
        FinancialStatement.statement_type == "SFP",
    ).all()
    for stmt in stmts:
        lines = stmt.lines
        total_assets = next((l.current_amount for l in lines if l.is_total and "TOTAL ASSETS" in l.label.upper()), None)
        total_liab_eq = next((l.current_amount for l in lines if l.is_total and "TOTAL LIABILITIES" in l.label.upper()), None)
        if total_assets is not None and total_liab_eq is not None:
            diff = abs((total_assets or Decimal(0)) - (total_liab_eq or Decimal(0)))
            if diff > Decimal("1.00"):
                _add_result(eng_id, "BALANCE_SHEET_EQUATION", ValidationSeverity.ERROR,
                    f"Balance sheet does not balance: difference of {diff:,.2f}",
                    f"Total Assets: {total_assets:,.2f} vs Total Liabilities & Equity: {total_liab_eq:,.2f}",
                    db)
            else:
                _add_result(eng_id, "BALANCE_SHEET_EQUATION", ValidationSeverity.INFO,
                    "Balance sheet equation checks out", None, db)


def check_unmapped_accounts(eng_id: int, db: Session) -> None:
    tbs = db.query(TrialBalance).filter(TrialBalance.engagement_id == eng_id, TrialBalance.status == "PROCESSED").all()
    for tb in tbs:
        unmapped = [l for l in tb.lines if not l.ifrs_category and not l.is_excluded]
        if unmapped:
            _add_result(eng_id, "UNMAPPED_ACCOUNTS", ValidationSeverity.WARNING,
                f"{len(unmapped)} account(s) not mapped to IFRS categories",
                "\n".join(f"- {l.account_code or ''} {l.account_name}" for l in unmapped[:10]),
                db)


def check_negative_unusual_balances(eng_id: int, db: Session) -> None:
    asset_categories = {"PPE", "RIGHT_OF_USE", "INTANGIBLES", "GOODWILL", "CASH", "TRADE_RECEIVABLES", "INVENTORIES"}
    liability_categories = {"TRADE_PAYABLES", "BORROWINGS_NC", "BORROWINGS_C", "TAX_PAYABLE"}
    tbs = db.query(TrialBalance).filter(TrialBalance.engagement_id == eng_id).all()
    for tb in tbs:
        for line in tb.lines:
            if not line.ifrs_category or line.is_excluded:
                continue
            bal = line.balance or Decimal(0)
            if line.ifrs_category in asset_categories and bal < Decimal("-0.01"):
                _add_result(eng_id, "NEGATIVE_BALANCE", ValidationSeverity.WARNING,
                    f"Unusual negative balance for asset account: {line.account_name}",
                    f"Balance: {bal:,.2f}", db)
            elif line.ifrs_category in liability_categories and bal > Decimal("0.01"):
                _add_result(eng_id, "UNUSUAL_BALANCE", ValidationSeverity.WARNING,
                    f"Unusual positive balance for liability account: {line.account_name}",
                    f"Balance: {bal:,.2f}", db)


def check_prior_year_consistency(eng_id: int, db: Session) -> None:
    eng = db.query(Engagement).filter(Engagement.id == eng_id).first()
    if not eng or not eng.comparative_year:
        return
    current_tbs = db.query(TrialBalance).filter(
        TrialBalance.engagement_id == eng_id, TrialBalance.is_comparative == False
    ).all()
    comparative_tbs = db.query(TrialBalance).filter(
        TrialBalance.engagement_id == eng_id, TrialBalance.is_comparative == True
    ).all()
    if not comparative_tbs:
        _add_result(eng_id, "MISSING_COMPARATIVE", ValidationSeverity.WARNING,
            f"Comparative year {eng.comparative_year} not uploaded",
            "Upload comparative trial balance for complete financial statements", db)


def check_required_disclosures(eng_id: int, db: Session) -> None:
    from app.models.disclosure import DisclosureNote, DisclosureType
    existing_types = {n.note_type for n in db.query(DisclosureNote).filter(DisclosureNote.engagement_id == eng_id).all()}
    required = {DisclosureType.ACCOUNTING_POLICIES}
    missing = required - existing_types
    for dt in missing:
        _add_result(eng_id, "MISSING_DISCLOSURE", ValidationSeverity.ERROR,
            f"Required disclosure missing: {dt.value.replace('_', ' ').title()}",
            "This disclosure is mandatory under IFRS", db)


def run_all_checks(eng_id: int, db: Session) -> list[ValidationResult]:
    _clear_existing(eng_id, db)
    check_unmapped_accounts(eng_id, db)
    check_balance_sheet_equation(eng_id, db)
    check_negative_unusual_balances(eng_id, db)
    check_prior_year_consistency(eng_id, db)
    check_required_disclosures(eng_id, db)
    db.commit()
    return db.query(ValidationResult).filter(ValidationResult.engagement_id == eng_id).all()
