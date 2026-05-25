# IFRS classification taxonomy - maps IFRSCategory to display labels, sections, and statement positions

IFRS_TAXONOMY = {
    # ── Statement of Financial Position ──────────────────────────────────────
    "SFP": {
        "NON-CURRENT ASSETS": {
            "PPE": {"label": "Property, plant and equipment", "normal_balance": "DR", "note": "3"},
            "RIGHT_OF_USE": {"label": "Right-of-use assets", "normal_balance": "DR", "note": "4"},
            "INTANGIBLES": {"label": "Intangible assets", "normal_balance": "DR", "note": "5"},
            "GOODWILL": {"label": "Goodwill", "normal_balance": "DR", "note": "6"},
            "INVESTMENTS_ASSOCIATES": {"label": "Investments in associates", "normal_balance": "DR"},
            "FINANCIAL_ASSETS_NC": {"label": "Financial assets", "normal_balance": "DR"},
            "DEFERRED_TAX_ASSET": {"label": "Deferred tax asset", "normal_balance": "DR", "note": "12"},
            "OTHER_NC_ASSETS": {"label": "Other non-current assets", "normal_balance": "DR"},
        },
        "CURRENT ASSETS": {
            "INVENTORIES": {"label": "Inventories", "normal_balance": "DR", "note": "7"},
            "TRADE_RECEIVABLES": {"label": "Trade and other receivables", "normal_balance": "DR", "note": "8"},
            "PREPAYMENTS": {"label": "Prepayments", "normal_balance": "DR"},
            "FINANCIAL_ASSETS_C": {"label": "Financial assets", "normal_balance": "DR"},
            "CASH": {"label": "Cash and cash equivalents", "normal_balance": "DR", "note": "9"},
            "OTHER_C_ASSETS": {"label": "Other current assets", "normal_balance": "DR"},
        },
        "NON-CURRENT LIABILITIES": {
            "BORROWINGS_NC": {"label": "Borrowings", "normal_balance": "CR", "note": "13"},
            "LEASE_LIABILITIES_NC": {"label": "Lease liabilities", "normal_balance": "CR", "note": "4"},
            "DEFERRED_TAX_LIABILITY": {"label": "Deferred tax liability", "normal_balance": "CR", "note": "12"},
            "EMPLOYEE_OBLIGATIONS": {"label": "Employee benefit obligations", "normal_balance": "CR"},
            "OTHER_NC_LIABILITIES": {"label": "Other non-current liabilities", "normal_balance": "CR"},
        },
        "CURRENT LIABILITIES": {
            "TRADE_PAYABLES": {"label": "Trade and other payables", "normal_balance": "CR", "note": "10"},
            "BORROWINGS_C": {"label": "Borrowings", "normal_balance": "CR", "note": "13"},
            "LEASE_LIABILITIES_C": {"label": "Lease liabilities", "normal_balance": "CR", "note": "4"},
            "TAX_PAYABLE": {"label": "Tax payable", "normal_balance": "CR", "note": "12"},
            "ACCRUALS": {"label": "Accruals", "normal_balance": "CR"},
            "OTHER_C_LIABILITIES": {"label": "Other current liabilities", "normal_balance": "CR"},
        },
        "EQUITY": {
            "SHARE_CAPITAL": {"label": "Share capital", "normal_balance": "CR", "note": "14"},
            "SHARE_PREMIUM": {"label": "Share premium", "normal_balance": "CR"},
            "OTHER_RESERVES": {"label": "Other reserves", "normal_balance": "CR"},
            "RETAINED_EARNINGS": {"label": "Retained earnings", "normal_balance": "CR"},
        },
    },
    # ── Profit & Loss ─────────────────────────────────────────────────────────
    "PL": {
        "REVENUE": {
            "REVENUE": {"label": "Revenue", "normal_balance": "CR", "note": "15"},
            "OTHER_INCOME": {"label": "Other income", "normal_balance": "CR"},
        },
        "OPERATING EXPENSES": {
            "COST_OF_SALES": {"label": "Cost of sales", "normal_balance": "DR"},
            "DISTRIBUTION_COSTS": {"label": "Distribution costs", "normal_balance": "DR"},
            "ADMIN_EXPENSES": {"label": "Administrative expenses", "normal_balance": "DR"},
            "OTHER_OP_EXPENSES": {"label": "Other operating expenses", "normal_balance": "DR"},
        },
        "FINANCE": {
            "FINANCE_INCOME": {"label": "Finance income", "normal_balance": "CR"},
            "FINANCE_COSTS": {"label": "Finance costs", "normal_balance": "DR"},
        },
        "TAX": {
            "INCOME_TAX": {"label": "Income tax expense", "normal_balance": "DR", "note": "12"},
        },
        "OCI": {
            "OCI": {"label": "Other comprehensive income", "normal_balance": "CR"},
        },
    },
}

# Keyword hints used by the AI mapper for initial classification
MAPPING_HINTS: dict[str, list[str]] = {
    "PPE": ["property", "plant", "equipment", "machinery", "vehicles", "furniture", "buildings", "land", "fixtures", "fittings", "leasehold improvements"],
    "RIGHT_OF_USE": ["right-of-use", "rou asset", "lease asset", "ifrs 16"],
    "INTANGIBLES": ["intangible", "software", "license", "patent", "trademark", "brand", "customer list", "development costs"],
    "GOODWILL": ["goodwill"],
    "INVENTORIES": ["inventory", "inventories", "stock", "goods", "raw materials", "work in progress", "finished goods", "wip"],
    "TRADE_RECEIVABLES": ["trade receivable", "accounts receivable", "debtors", "receivable", "ar ", "a/r"],
    "PREPAYMENTS": ["prepayment", "prepaid", "advance payment", "deposits paid"],
    "CASH": ["cash", "bank", "petty cash", "current account", "savings account", "short-term deposits"],
    "TRADE_PAYABLES": ["trade payable", "accounts payable", "creditors", "payable", "ap ", "a/p"],
    "BORROWINGS_NC": ["long-term loan", "long term borrowing", "term loan", "mortgage", "bond", "debenture"],
    "BORROWINGS_C": ["bank overdraft", "overdraft", "short-term loan", "current portion", "revolving credit"],
    "TAX_PAYABLE": ["tax payable", "income tax payable", "corporation tax", "vat payable"],
    "DEFERRED_TAX_ASSET": ["deferred tax asset", "dta"],
    "DEFERRED_TAX_LIABILITY": ["deferred tax liability", "dtl"],
    "SHARE_CAPITAL": ["share capital", "common stock", "ordinary shares", "issued capital", "paid-up capital"],
    "SHARE_PREMIUM": ["share premium", "additional paid-in capital", "capital surplus"],
    "RETAINED_EARNINGS": ["retained earnings", "retained profit", "accumulated profit", "profit and loss account", "accumulated deficit"],
    "OTHER_RESERVES": ["reserve", "revaluation reserve", "fair value reserve", "translation reserve"],
    "REVENUE": ["revenue", "sales", "turnover", "income from operations", "service revenue", "rental income"],
    "COST_OF_SALES": ["cost of sales", "cost of goods sold", "cogs", "direct costs", "cost of revenue"],
    "ADMIN_EXPENSES": ["administrative", "admin", "general expenses", "overhead", "management fees", "salaries", "wages", "staff costs", "depreciation", "amortisation", "rent", "utilities"],
    "DISTRIBUTION_COSTS": ["distribution", "selling expenses", "marketing", "advertising", "delivery costs"],
    "FINANCE_INCOME": ["interest income", "finance income", "investment income", "dividend income"],
    "FINANCE_COSTS": ["interest expense", "finance costs", "interest payable", "bank charges", "borrowing costs"],
    "INCOME_TAX": ["income tax", "corporation tax", "tax charge", "tax expense", "current tax"],
    "ACCRUALS": ["accrual", "accrued", "accrued expenses", "accrued liabilities"],
    "LEASE_LIABILITIES_NC": ["lease liability", "finance lease", "operating lease", "ifrs 16 liability"],
    "LEASE_LIABILITIES_C": ["current lease", "current portion of lease"],
}
