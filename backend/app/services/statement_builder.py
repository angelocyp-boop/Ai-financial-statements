"""IFRS financial statement builder - aggregates TB lines into structured statements."""
from __future__ import annotations
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.trial_balance import TBLine, TrialBalance
from app.models.statement import FinancialStatement, StatementLine, StatementType
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


def _v(totals: dict, key: str) -> Decimal:
    """Absolute value of a category total, defaulting to zero."""
    return abs(totals.get(key, Decimal(0)))


def _calc_profit(
    current_totals: dict,
    comp_totals: dict,
) -> tuple[Decimal, Decimal]:
    """Return (profit_current, profit_comparative) net of tax."""
    def _profit(t):
        revenue = _v(t, "REVENUE") + _v(t, "OTHER_INCOME")
        opex = _v(t, "COST_OF_SALES") + _v(t, "DISTRIBUTION_COSTS") + _v(t, "ADMIN_EXPENSES") + _v(t, "OTHER_OP_EXPENSES")
        fi = _v(t, "FINANCE_INCOME")
        fc = _v(t, "FINANCE_COSTS")
        tax = _v(t, "INCOME_TAX")
        return revenue - opex + fi - fc - tax
    return _profit(current_totals), _profit(comp_totals)


def _build_sfp(
    eng_id: int,
    stmt_id: int,
    current_totals: dict,
    comp_totals: dict,
    db: Session,
) -> None:
    taxonomy = IFRS_TAXONOMY["SFP"]
    order = 0

    total_assets_curr = Decimal(0)
    total_assets_comp = Decimal(0)
    total_liab_equity_curr = Decimal(0)
    total_liab_equity_comp = Decimal(0)

    for section in ["NON-CURRENT ASSETS", "CURRENT ASSETS"]:
        section_curr = Decimal(0)
        section_comp = Decimal(0)
        db.add(StatementLine(
            statement_id=stmt_id, section=section, label=section,
            is_header=True, is_bold=True, indent_level=0, order=order,
        ))
        order += 1
        for cat, meta in taxonomy[section].items():
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
            statement_id=stmt_id, section=section,
            label=f"Total {section.title()}",
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
        db.add(StatementLine(
            statement_id=stmt_id, section=section, label=section,
            is_header=True, is_bold=True, indent_level=0, order=order,
        ))
        order += 1
        for cat, meta in taxonomy[section].items():
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
            statement_id=stmt_id, section=section,
            label=f"Total {section.title()}",
            current_amount=section_curr, comparative_amount=section_comp,
            is_subtotal=True, is_bold=True, indent_level=0, order=order,
        ))
        total_liab_equity_curr += section_curr
        total_liab_equity_comp += section_comp
        order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="LIABILITIES AND EQUITY",
        label="TOTAL LIABILITIES AND EQUITY",
        current_amount=total_liab_equity_curr, comparative_amount=total_liab_equity_comp,
        is_total=True, is_bold=True, indent_level=0, order=order,
    ))


def _build_pl(
    eng_id: int,
    stmt_id: int,
    current_totals: dict,
    comp_totals: dict,
    db: Session,
) -> None:
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
        db.add(StatementLine(
            statement_id=stmt_id, section=section, label=section,
            is_header=True, is_bold=True, indent_level=0, order=order,
        ))
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
                    revenue_curr += curr_val
                    revenue_comp += comp_val
                elif cat in ("COST_OF_SALES", "DISTRIBUTION_COSTS", "ADMIN_EXPENSES", "OTHER_OP_EXPENSES"):
                    expenses_curr += curr_val
                    expenses_comp += comp_val
                elif cat == "FINANCE_INCOME":
                    finance_income_curr += curr_val
                    finance_income_comp += comp_val
                elif cat == "FINANCE_COSTS":
                    finance_costs_curr += curr_val
                    finance_costs_comp += comp_val
                elif cat == "INCOME_TAX":
                    tax_curr += curr_val
                    tax_comp += comp_val

    cogs_curr = abs(current_totals.get("COST_OF_SALES", Decimal(0)))
    cogs_comp = abs(comp_totals.get("COST_OF_SALES", Decimal(0)))
    gross_curr = revenue_curr - cogs_curr
    gross_comp = revenue_comp - cogs_comp
    ebit_curr = gross_curr - (expenses_curr - cogs_curr)
    ebit_comp = gross_comp - (expenses_comp - cogs_comp)
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


def _build_cash_flow(
    eng_id: int,
    stmt_id: int,
    current_totals: dict,
    comp_totals: dict,
    db: Session,
) -> None:
    """Cash flow statement - indirect method per IAS 7."""
    profit_curr, profit_comp = _calc_profit(current_totals, comp_totals)

    fi_curr = _v(current_totals, "FINANCE_INCOME")
    fi_comp = _v(comp_totals, "FINANCE_INCOME")
    fc_curr = _v(current_totals, "FINANCE_COSTS")
    fc_comp = _v(comp_totals, "FINANCE_COSTS")
    tax_curr = _v(current_totals, "INCOME_TAX")
    tax_comp = _v(comp_totals, "INCOME_TAX")

    order = 0

    # ── OPERATING ────────────────────────────────────────────────────────────
    db.add(StatementLine(
        statement_id=stmt_id, section="OPERATING",
        label="CASH FLOWS FROM OPERATING ACTIVITIES",
        is_header=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="OPERATING", label="Profit for the year",
        current_amount=profit_curr, comparative_amount=profit_comp,
        is_bold=True, indent_level=1, order=order,
    ))
    order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="OPERATING", label="Adjustments for:",
        is_header=True, indent_level=1, order=order,
    ))
    order += 1

    # Add back finance costs (deducted in profit but classified in financing)
    if fc_curr or fc_comp:
        db.add(StatementLine(
            statement_id=stmt_id, section="OPERATING", label="Finance costs",
            current_amount=fc_curr, comparative_amount=fc_comp,
            indent_level=2, order=order,
        ))
        order += 1

    # Remove finance income (included in profit but classified in investing)
    if fi_curr or fi_comp:
        db.add(StatementLine(
            statement_id=stmt_id, section="OPERATING", label="Finance income",
            current_amount=-fi_curr, comparative_amount=-fi_comp,
            indent_level=2, order=order,
        ))
        order += 1

    # Changes in working capital
    db.add(StatementLine(
        statement_id=stmt_id, section="OPERATING", label="Changes in working capital:",
        is_header=True, indent_level=1, order=order,
    ))
    order += 1

    # For assets: increase = cash outflow (negative); decrease = inflow (positive)
    # For liabilities: increase = cash inflow (positive); decrease = outflow (negative)
    wc_items = [
        ("INVENTORIES",        "Inventories",                      -1),
        ("TRADE_RECEIVABLES",  "Trade and other receivables",      -1),
        ("PREPAYMENTS",        "Prepayments and other assets",     -1),
        ("OTHER_C_ASSETS",     "Other current assets",             -1),
        ("TRADE_PAYABLES",     "Trade and other payables",          1),
        ("ACCRUALS",           "Accruals and other liabilities",    1),
        ("OTHER_C_LIABILITIES","Other current liabilities",         1),
        ("TAX_PAYABLE",        "Tax payable",                       1),
    ]

    total_wc_curr = Decimal(0)
    total_wc_comp = Decimal(0)
    for cat, label, direction in wc_items:
        curr_bal = _v(current_totals, cat)
        comp_bal = _v(comp_totals, cat)
        if not curr_bal and not comp_bal:
            continue
        # Change vs prior year: asset increase is outflow; liability increase is inflow
        change_curr = (curr_bal - comp_bal) * direction
        change_comp = Decimal(0)  # prior-year comparative change not derivable from a single TB
        db.add(StatementLine(
            statement_id=stmt_id, section="OPERATING", label=label,
            current_amount=change_curr, comparative_amount=change_comp,
            indent_level=2, order=order,
        ))
        total_wc_curr += change_curr
        order += 1

    # Cash generated from operations = profit + fc - fi + WC changes
    # (tax and interest will be shown separately below)
    cash_gen_curr = profit_curr + fc_curr - fi_curr + total_wc_curr
    cash_gen_comp = profit_comp + fc_comp - fi_comp + total_wc_comp

    db.add(StatementLine(
        statement_id=stmt_id, section="OPERATING",
        label="Cash generated from operations",
        current_amount=cash_gen_curr, comparative_amount=cash_gen_comp,
        is_subtotal=True, is_bold=True, indent_level=1, order=order,
    ))
    order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="OPERATING", label="Income tax paid",
        current_amount=-tax_curr, comparative_amount=-tax_comp,
        indent_level=1, order=order,
    ))
    order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="OPERATING", label="Interest paid",
        current_amount=-fc_curr, comparative_amount=-fc_comp,
        indent_level=1, order=order,
    ))
    order += 1

    if fi_curr or fi_comp:
        db.add(StatementLine(
            statement_id=stmt_id, section="OPERATING", label="Interest received",
            current_amount=fi_curr, comparative_amount=fi_comp,
            indent_level=1, order=order,
        ))
        order += 1

    net_op_curr = cash_gen_curr - tax_curr - fc_curr + fi_curr
    net_op_comp = cash_gen_comp - tax_comp - fc_comp + fi_comp

    db.add(StatementLine(
        statement_id=stmt_id, section="OPERATING",
        label="Net cash from operating activities",
        current_amount=net_op_curr, comparative_amount=net_op_comp,
        is_subtotal=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1

    # ── INVESTING ────────────────────────────────────────────────────────────
    db.add(StatementLine(
        statement_id=stmt_id, section="INVESTING",
        label="CASH FLOWS FROM INVESTING ACTIVITIES",
        is_header=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1

    invest_items = [
        ("PPE",              "INVESTING", "Purchase of property, plant and equipment", -1),
        ("INTANGIBLES",      "INVESTING", "Purchase of intangible assets",             -1),
        ("RIGHT_OF_USE",     "INVESTING", "Acquisition of right-of-use assets",        -1),
        ("FINANCIAL_ASSETS_NC", "INVESTING", "Purchase of financial assets",           -1),
    ]

    net_invest_curr = Decimal(0)
    net_invest_comp = Decimal(0)

    for cat, sec, label, direction in invest_items:
        curr_bal = _v(current_totals, cat)
        comp_bal = _v(comp_totals, cat)
        if not curr_bal and not comp_bal:
            continue
        # Net capex ≈ change in balance (increase = purchase = outflow)
        change_curr = (curr_bal - comp_bal) * direction
        if change_curr == 0:
            continue
        db.add(StatementLine(
            statement_id=stmt_id, section=sec, label=label,
            current_amount=change_curr, comparative_amount=Decimal(0),
            indent_level=1, order=order,
        ))
        net_invest_curr += change_curr
        order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="INVESTING",
        label="Net cash used in investing activities",
        current_amount=net_invest_curr, comparative_amount=net_invest_comp,
        is_subtotal=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1

    # ── FINANCING ────────────────────────────────────────────────────────────
    db.add(StatementLine(
        statement_id=stmt_id, section="FINANCING",
        label="CASH FLOWS FROM FINANCING ACTIVITIES",
        is_header=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1

    borr_curr = _v(current_totals, "BORROWINGS_NC") + _v(current_totals, "BORROWINGS_C")
    borr_comp = _v(comp_totals, "BORROWINGS_NC") + _v(comp_totals, "BORROWINGS_C")
    borr_change = borr_curr - borr_comp
    lease_curr = _v(current_totals, "LEASE_LIABILITIES_NC") + _v(current_totals, "LEASE_LIABILITIES_C")
    lease_comp = _v(comp_totals, "LEASE_LIABILITIES_NC") + _v(comp_totals, "LEASE_LIABILITIES_C")
    lease_change = lease_curr - lease_comp
    eq_curr = _v(current_totals, "SHARE_CAPITAL") + _v(current_totals, "SHARE_PREMIUM")
    eq_comp = _v(comp_totals, "SHARE_CAPITAL") + _v(comp_totals, "SHARE_PREMIUM")
    equity_raised = eq_curr - eq_comp

    net_fin_curr = Decimal(0)

    if borr_change:
        label_borr = "Proceeds from borrowings" if borr_change > 0 else "Repayment of borrowings"
        db.add(StatementLine(
            statement_id=stmt_id, section="FINANCING", label=label_borr,
            current_amount=borr_change, comparative_amount=Decimal(0),
            indent_level=1, order=order,
        ))
        net_fin_curr += borr_change
        order += 1

    if lease_change:
        label_lease = "Proceeds from new leases" if lease_change > 0 else "Payment of lease liabilities"
        db.add(StatementLine(
            statement_id=stmt_id, section="FINANCING", label=label_lease,
            current_amount=lease_change, comparative_amount=Decimal(0),
            indent_level=1, order=order,
        ))
        net_fin_curr += lease_change
        order += 1

    if equity_raised > 0:
        db.add(StatementLine(
            statement_id=stmt_id, section="FINANCING",
            label="Proceeds from issue of share capital",
            current_amount=equity_raised, comparative_amount=Decimal(0),
            indent_level=1, order=order,
        ))
        net_fin_curr += equity_raised
        order += 1

    # Estimate dividends paid: retained earnings change net of profit for the year
    re_curr = _v(current_totals, "RETAINED_EARNINGS")
    re_comp = _v(comp_totals, "RETAINED_EARNINGS")
    re_change = re_curr - re_comp
    dividends = re_change - profit_curr  # positive profit less RE growth = distributions
    if dividends < 0:  # distributions were made
        db.add(StatementLine(
            statement_id=stmt_id, section="FINANCING", label="Dividends paid",
            current_amount=dividends, comparative_amount=Decimal(0),
            indent_level=1, order=order,
        ))
        net_fin_curr += dividends
        order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="FINANCING",
        label="Net cash from financing activities",
        current_amount=net_fin_curr, comparative_amount=Decimal(0),
        is_subtotal=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1

    # ── NET CASH MOVEMENT ────────────────────────────────────────────────────
    cash_curr = _v(current_totals, "CASH")
    cash_comp = _v(comp_totals, "CASH")
    net_movement = net_op_curr + net_invest_curr + net_fin_curr

    db.add(StatementLine(
        statement_id=stmt_id, section="CASH",
        label="Net (decrease)/increase in cash and cash equivalents",
        current_amount=net_movement, comparative_amount=Decimal(0),
        is_subtotal=True, is_bold=True, indent_level=0, order=order,
    ))
    order += 1
    db.add(StatementLine(
        statement_id=stmt_id, section="CASH",
        label="Cash and cash equivalents at beginning of year",
        current_amount=cash_comp, comparative_amount=Decimal(0),
        indent_level=1, order=order,
    ))
    order += 1
    db.add(StatementLine(
        statement_id=stmt_id, section="CASH",
        label="Cash and cash equivalents at end of year",
        current_amount=cash_curr, comparative_amount=Decimal(0),
        is_total=True, is_bold=True, indent_level=0, order=order,
    ))


def _build_equity(
    eng_id: int,
    stmt_id: int,
    current_totals: dict,
    comp_totals: dict,
    db: Session,
) -> None:
    """Statement of changes in equity per IAS 1."""
    profit_curr, profit_comp = _calc_profit(current_totals, comp_totals)
    oci_curr = _v(current_totals, "OCI")
    oci_comp = _v(comp_totals, "OCI")

    order = 0

    components = [
        ("SHARE_CAPITAL",    "Share capital"),
        ("SHARE_PREMIUM",    "Share premium"),
        ("OTHER_RESERVES",   "Other reserves"),
        ("RETAINED_EARNINGS","Retained earnings"),
    ]

    # Per-component section showing opening → movements → closing
    for cat, comp_label in components:
        curr_bal = _v(current_totals, cat)
        comp_bal = _v(comp_totals, cat)
        if not curr_bal and not comp_bal:
            continue

        section = comp_label.upper()
        db.add(StatementLine(
            statement_id=stmt_id, section=section, label=section,
            is_header=True, is_bold=True, indent_level=0, order=order,
        ))
        order += 1

        db.add(StatementLine(
            statement_id=stmt_id, section=section, label="Balance at beginning of year",
            current_amount=comp_bal, comparative_amount=Decimal(0),
            indent_level=1, order=order,
        ))
        order += 1

        if cat == "RETAINED_EARNINGS":
            db.add(StatementLine(
                statement_id=stmt_id, section=section, label="Profit for the year",
                current_amount=profit_curr, comparative_amount=Decimal(0),
                indent_level=1, order=order,
            ))
            order += 1
            if oci_curr:
                db.add(StatementLine(
                    statement_id=stmt_id, section=section,
                    label="Other comprehensive income",
                    current_amount=oci_curr, comparative_amount=Decimal(0),
                    indent_level=1, order=order,
                ))
                order += 1
            # Dividends = implied from RE change net of profit
            dividends = (curr_bal - comp_bal) - profit_curr - oci_curr
            if dividends < 0:
                db.add(StatementLine(
                    statement_id=stmt_id, section=section, label="Dividends declared",
                    current_amount=dividends, comparative_amount=Decimal(0),
                    indent_level=1, order=order,
                ))
                order += 1
        elif cat == "SHARE_CAPITAL":
            issued = curr_bal - comp_bal
            if issued:
                db.add(StatementLine(
                    statement_id=stmt_id, section=section, label="Issue of ordinary shares",
                    current_amount=issued, comparative_amount=Decimal(0),
                    indent_level=1, order=order,
                ))
                order += 1
        elif cat == "SHARE_PREMIUM":
            prem_change = curr_bal - comp_bal
            if prem_change:
                db.add(StatementLine(
                    statement_id=stmt_id, section=section, label="Share premium on issue",
                    current_amount=prem_change, comparative_amount=Decimal(0),
                    indent_level=1, order=order,
                ))
                order += 1
        elif cat == "OTHER_RESERVES":
            res_change = curr_bal - comp_bal
            if res_change:
                db.add(StatementLine(
                    statement_id=stmt_id, section=section,
                    label="Movement in other reserves",
                    current_amount=res_change, comparative_amount=Decimal(0),
                    indent_level=1, order=order,
                ))
                order += 1

        db.add(StatementLine(
            statement_id=stmt_id, section=section, label="Balance at end of year",
            current_amount=curr_bal, comparative_amount=Decimal(0),
            is_subtotal=True, is_bold=True, indent_level=0, order=order,
        ))
        order += 1

    # ── TOTAL EQUITY ────────────────────────────────────────────────────────
    total_curr = sum(_v(current_totals, c) for c, _ in components)
    total_comp = sum(_v(comp_totals, c) for c, _ in components)
    total_movement = total_curr - total_comp

    db.add(StatementLine(
        statement_id=stmt_id, section="TOTAL EQUITY",
        label="TOTAL EQUITY", is_header=True, is_bold=True,
        indent_level=0, order=order,
    ))
    order += 1
    db.add(StatementLine(
        statement_id=stmt_id, section="TOTAL EQUITY",
        label="Balance at beginning of year",
        current_amount=total_comp, comparative_amount=Decimal(0),
        indent_level=1, order=order,
    ))
    order += 1
    db.add(StatementLine(
        statement_id=stmt_id, section="TOTAL EQUITY",
        label="Total comprehensive income",
        current_amount=profit_curr + oci_curr, comparative_amount=Decimal(0),
        indent_level=1, order=order,
    ))
    order += 1

    # Total distributions / equity transactions
    other_movements = total_movement - profit_curr - oci_curr
    if other_movements:
        db.add(StatementLine(
            statement_id=stmt_id, section="TOTAL EQUITY",
            label="Other equity movements (net)",
            current_amount=other_movements, comparative_amount=Decimal(0),
            indent_level=1, order=order,
        ))
        order += 1

    db.add(StatementLine(
        statement_id=stmt_id, section="TOTAL EQUITY",
        label="Balance at end of year",
        current_amount=total_curr, comparative_amount=Decimal(0),
        is_total=True, is_bold=True, indent_level=0, order=order,
    ))


def build_statements(
    eng_id: int,
    statement_types: list[str],
    db: Session,
) -> list[FinancialStatement]:
    current_lines, comp_lines = _get_tb_lines(eng_id, db)
    current_totals = _sum_by_category(current_lines)
    comp_totals = _sum_by_category(comp_lines)

    # Remove any previously generated statements for this engagement
    existing = db.query(FinancialStatement).filter(
        FinancialStatement.engagement_id == eng_id
    ).all()
    for e in existing:
        db.delete(e)
    db.flush()

    results = []
    builder_map = {
        StatementType.SFP:       _build_sfp,
        StatementType.PL:        _build_pl,
        StatementType.CASH_FLOW: _build_cash_flow,
        StatementType.EQUITY:    _build_equity,
    }

    for stype_str in statement_types:
        try:
            st = StatementType(stype_str)
        except ValueError:
            continue

        stmt = FinancialStatement(
            engagement_id=eng_id,
            statement_type=st,
            generated_at=datetime.utcnow(),
        )
        db.add(stmt)
        db.flush()

        builder = builder_map[st]
        builder(eng_id, stmt.id, current_totals, comp_totals, db)

        db.commit()
        db.refresh(stmt)
        results.append(stmt)

    return results
