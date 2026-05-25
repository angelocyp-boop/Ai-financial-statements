"""IFRS financial statement builder - aggregates TB lines into structured statements."""
from __future__ import annotations
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import Session
from app.models.trial_balance import TBLine, TrialBalance
from app.models.statement import FinancialStatement, StatementLine, StatementType
from app.models.engagement import Engagement
from app.services.ifrs_taxonomy import IFRS_TAXONOMY


def _get_tb_lines(eng_id: int, db: Session) -> tuple[list[TBLine], list[TBLine]]:
    tbs = db.query(TrialBalance).filter(
        TrialBalance.engagement_id == eng_id,
        TrialBalance.status == "PROCESSED",
    ).all()
    current = []
    comparative = []
    for tb in tbs:
        for line in tb.lines:
            if not line.is_excluded and line.ifrs_category:
                if line.is_comparative:
                    comparative.append(line)
                else:
                    current.append(line)
    return current, comparative


def _sum_by_category(lines: list[TBLine]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for line in lines:
        if line.ifrs_category:
            totals[line.ifrs_category] = totals.get(line.ifrs_category, Decimal(0)) + (line.balance or Decimal(0))
    return totals


def _build_sfp(eng_id: int, stmt_id: int, current_totals: dict, comp_totals: dict, db: Session) -> None:
    taxonomy = IFRS_TAXONOMY["SFP"]
    order = 0
    section_order = {
        "NON-CURRENT ASSETS": 0, "CURRENT ASSETS": 1,
        "NON-CURRENT LIABILITIES": 2, "CURRENT LIABILITIES": 3, "EQUITY": 4
    }
    asset_sections = {"NON-CURRENT ASSETS", "CURRENT ASSETS"}
    liability_sections = {"NON-CURRENT LIABILITIES", "CURRENT LIABILITIES", "EQUITY"}

    total_assets_curr = Decimal(0)
    total_assets_comp = Decimal(0)
    total_liab_equity_curr = Decimal(0)
    total_liab_equity_comp = Decimal(0)

    for section in ["NON-CURRENT ASSETS", "CURRENT ASSETS"]:
        section_curr = Decimal(0)
        section_comp = Decimal(0)
        db.add(StatementLine(statement_id=stmt_id, section=section, label=section, is_header=True, is_bold=True, indent_level=0, order=order))
        order += 1
        items = taxonomy[section]
        for cat, meta in items.items():
            curr = current_totals.get(cat)
            comp = comp_totals.get(cat)
            if curr is not None or comp is not None:
                curr_val = abs(curr or Decimal(0))
                comp_val = abs(comp or Decimal(0))
                db.add(StatementLine(
                    statement_id=stmt_id, section=section, label=meta["label"],
                    current_amount=curr_val, comparative_amount=comp_val,
                    note_reference=meta.get("note"), indent_level=1, order=order,
                ))
                section_curr += curr_val
                section_comp += comp_val
                order += 1
        db.add(StatementLine(
            statement_id=stmt_id, section=section, label=f"Total {section.title()}",
            current_amount=section_curr, comparative_amount=section_comp,
            is_subtotal=True, is_bold=True, indent_level=0, order=order,
        ))
        total_assets_curr += section_curr
        total_assets_comp += section_comp
        order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="ASSETS", label="TOTAL ASSETS",
        current_amount=total_assets_curr, comparative_amount=total_assets_comp,
        is_total=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1

    for section in ["NON-CURRENT LIABILITIES", "CURRENT LIABILITIES", "EQUITY"]:
        section_curr = Decimal(0)
        section_comp = Decimal(0)
        db.add(StatementLine(statement_id=stmt_id, section=section, label=section, is_header=True, is_bold=True, indent_level=0, order=order))
        order += 1
        items = taxonomy[section]
        for cat, meta in items.items():
            curr = current_totals.get(cat)
            comp = comp_totals.get(cat)
            if curr is not None or comp is not None:
                curr_val = abs(curr or Decimal(0))
                comp_val = abs(comp or Decimal(0))
                db.add(StatementLine(
                    statement_id=stmt_id, section=section, label=meta["label"],
                    current_amount=curr_val, comparative_amount=comp_val,
                    note_reference=meta.get("note"), indent_level=1, order=order,
                ))
                section_curr += curr_val
                section_comp += comp_val
                order += 1
        db.add(StatementLine(
            statement_id=stmt_id, section=section, label=f"Total {section.title()}",
            current_amount=section_curr, comparative_amount=section_comp,
            is_subtotal=True, is_bold=True, indent_level=0, order=order,
        ))
        total_liab_equity_curr += section_curr
        total_liab_equity_comp += section_comp
        order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="LIABILITIES AND EQUITY", label="TOTAL LIABILITIES AND EQUITY",
        current_amount=total_liab_equity_curr, comparative_amount=total_liab_equity_comp,
        is_total=True, is_bold=True, indent_level=0, order=order,
    ))


def _build_pl(eng_id: int, stmt_id: int, current_totals: dict, comp_totals: dict, db: Session) -> None:
    taxonomy = IFRS_TAXONOMY["PL"]
    order = 0
    revenue_curr = Decimal(0)
    revenue_comp = Decimal(0)
    expenses_curr = Decimal(0)
    expenses_comp = Decimal(0)
    finance_income_curr = Decimal(0)
    finance_income_comp = Decimal(0)
    finance_costs_curr = Decimal(0)
    finance_costs_comp = Decimal(0)
    tax_curr = Decimal(0)
    tax_comp = Decimal(0)

    for section, items in taxonomy.items():
        db.add(StatementLine(statement_id=stmt_id, section=section, label=section, is_header=True, is_bold=True, indent_level=0, order=order))
        order += 1
        for cat, meta in items.items():
            curr = current_totals.get(cat)
            comp = comp_totals.get(cat)
            if curr is not None or comp is not None:
                curr_val = abs(curr or Decimal(0))
                comp_val = abs(comp or Decimal(0))
                db.add(StatementLine(
                    statement_id=stmt_id, section=section, label=meta["label"],
                    current_amount=curr_val, comparative_amount=comp_val,
                    note_reference=meta.get("note"), indent_level=1, order=order,
                ))
                order += 1
                if cat in ("REVENUE", "OTHER_INCOME"):
                    revenue_curr += curr_val; revenue_comp += comp_val
                elif cat in ("COST_OF_SALES", "DISTRIBUTION_COSTS", "ADMIN_EXPENSES", "OTHER_OP_EXPENSES"):
                    expenses_curr += curr_val; expenses_comp += comp_val
                elif cat == "FINANCE_INCOME":
                    finance_income_curr += curr_val; finance_income_comp += comp_val
                elif cat == "FINANCE_COSTS":
                    finance_costs_curr += curr_val; finance_costs_comp += comp_val
                elif cat == "INCOME_TAX":
                    tax_curr += curr_val; tax_comp += comp_val

    gross_curr = revenue_curr - current_totals.get("COST_OF_SALES", Decimal(0)).__abs__()
    gross_comp = revenue_comp - comp_totals.get("COST_OF_SALES", Decimal(0)).__abs__()
    ebit_curr = gross_curr - (expenses_curr - abs(current_totals.get("COST_OF_SALES", Decimal(0))))
    ebit_comp = gross_comp - (expenses_comp - abs(comp_totals.get("COST_OF_SALES", Decimal(0))))
    pbt_curr = ebit_curr + finance_income_curr - finance_costs_curr
    pbt_comp = ebit_comp + finance_income_comp - finance_costs_comp
    profit_curr = pbt_curr - tax_curr
    profit_comp = pbt_comp - tax_comp

    db.add(StatementLine(
        statement_id=stmt_id, section="PROFIT", label="Gross profit",
        current_amount=max(gross_curr, Decimal(0)), comparative_amount=max(gross_comp, Decimal(0)),
        is_subtotal=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1
    db.add(StatementLine(
        statement_id=stmt_id, section="PROFIT", label="Operating profit (EBIT)",
        current_amount=ebit_curr, comparative_amount=ebit_comp,
        is_subtotal=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1
    db.add(StatementLine(
        statement_id=stmt_id, section="PROFIT", label="Profit before tax",
        current_amount=pbt_curr, comparative_amount=pbt_comp,
        is_subtotal=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1
    db.add(StatementLine(
        statement_id=stmt_id, section="PROFIT", label="Profit for the year",
        current_amount=profit_curr, comparative_amount=profit_comp,
        is_total=True, is_bold=True, indent_level=0, order=order,
    ))


def build_statements(eng_id: int, statement_types: list[str], db: Session) -> list[FinancialStatement]:
    current_lines, comp_lines = _get_tb_lines(eng_id, db)
    current_totals = _sum_by_category(current_lines)
    comp_totals = _sum_by_category(comp_lines)

    existing = db.query(FinancialStatement).filter(FinancialStatement.engagement_id == eng_id).all()
    for e in existing:
        db.delete(e)
    db.flush()

    results = []
    for stype in statement_types:
        try:
            st = StatementType(stype)
        except ValueError:
            continue
        stmt = FinancialStatement(
            engagement_id=eng_id,
            statement_type=st,
            generated_at=datetime.utcnow(),
        )
        db.add(stmt)
        db.flush()

        if st == StatementType.SFP:
            _build_sfp(eng_id, stmt.id, current_totals, comp_totals, db)
        elif st == StatementType.PL:
            _build_pl(eng_id, stmt.id, current_totals, comp_totals, db)

        db.commit()
        db.refresh(stmt)
        results.append(stmt)

    return results
