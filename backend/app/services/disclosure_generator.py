"""AI-powered disclosure note generator."""
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.disclosure import DisclosureNote, DisclosureType
from app.models.engagement import Engagement
from app.models.trial_balance import TBLine, TrialBalance


DISCLOSURE_ORDER = [
    DisclosureType.ACCOUNTING_POLICIES,
    DisclosureType.PPE,
    DisclosureType.INTANGIBLES,
    DisclosureType.BORROWINGS,
    DisclosureType.LEASES,
    DisclosureType.REVENUE,
    DisclosureType.TAXATION,
    DisclosureType.SHARE_CAPITAL,
    DisclosureType.RELATED_PARTIES,
    DisclosureType.COMMITMENTS,
    DisclosureType.EVENTS_AFTER_REPORTING,
]


def _get_categories_in_use(eng_id: int, db: Session) -> set[str]:
    tbs = db.query(TrialBalance).filter(TrialBalance.engagement_id == eng_id).all()
    categories = set()
    for tb in tbs:
        for line in tb.lines:
            if line.ifrs_category:
                categories.add(line.ifrs_category)
    return categories


def _disclosure_needed(dtype: DisclosureType, categories: set[str]) -> bool:
    mapping = {
        DisclosureType.PPE: {"PPE", "RIGHT_OF_USE"},
        DisclosureType.INTANGIBLES: {"INTANGIBLES", "GOODWILL"},
        DisclosureType.BORROWINGS: {"BORROWINGS_NC", "BORROWINGS_C"},
        DisclosureType.LEASES: {"LEASE_LIABILITIES_NC", "LEASE_LIABILITIES_C", "RIGHT_OF_USE"},
        DisclosureType.REVENUE: {"REVENUE"},
        DisclosureType.TAXATION: {"INCOME_TAX", "TAX_PAYABLE", "DEFERRED_TAX_ASSET", "DEFERRED_TAX_LIABILITY"},
        DisclosureType.SHARE_CAPITAL: {"SHARE_CAPITAL", "SHARE_PREMIUM"},
        DisclosureType.ACCOUNTING_POLICIES: None,  # Always required
        DisclosureType.RELATED_PARTIES: None,
        DisclosureType.COMMITMENTS: None,
        DisclosureType.EVENTS_AFTER_REPORTING: None,
    }
    required = mapping.get(dtype)
    if required is None:
        return True
    return bool(categories & required)


def _generate_static_content(dtype: DisclosureType, eng: Engagement) -> str:
    year = eng.year
    client_name = eng.client.name if eng.client else "the Company"
    standard = eng.reporting_standard.value

    templates = {
        DisclosureType.ACCOUNTING_POLICIES: f"""<h3>Basis of Preparation</h3>
<p>The financial statements of {client_name} for the year ended {eng.period_end.strftime('%d %B %Y')} have been prepared in accordance with {standard} as adopted by the European Union.</p>
<p>The financial statements have been prepared under the historical cost convention, except where modified by the revaluation of certain financial instruments measured at fair value.</p>

<h3>Going Concern</h3>
<p>The directors have reviewed the Company's financial position and future prospects and have a reasonable expectation that the Company has adequate resources to continue in operational existence for the foreseeable future. Accordingly, the financial statements continue to be prepared on the going concern basis.</p>

<h3>Functional and Presentation Currency</h3>
<p>The financial statements are presented in {eng.currency}, which is also the functional currency of the Company. All amounts are rounded to the nearest euro unless otherwise stated.</p>

<h3>Use of Estimates and Judgements</h3>
<p>The preparation of financial statements requires management to make judgements, estimates and assumptions that affect the application of accounting policies and the reported amounts of assets, liabilities, income and expenses. Actual results may differ from these estimates.</p>""",

        DisclosureType.PPE: f"""<h3>Recognition and Measurement</h3>
<p>Items of property, plant and equipment are measured at cost less accumulated depreciation and accumulated impairment losses.</p>
<p>Cost includes expenditure that is directly attributable to the acquisition of the asset. Subsequent costs are included in the asset's carrying amount only when it is probable that future economic benefits associated with the item will flow to the Company.</p>

<h3>Depreciation</h3>
<p>Depreciation is calculated on a straight-line basis over the estimated useful lives of the assets:</p>
<ul>
<li>Buildings: 20-50 years</li>
<li>Machinery and equipment: 5-15 years</li>
<li>Motor vehicles: 4-6 years</li>
<li>Furniture and fixtures: 5-10 years</li>
<li>Computer equipment: 3-5 years</li>
</ul>""",

        DisclosureType.REVENUE: f"""<h3>Revenue Recognition</h3>
<p>Revenue is recognised in accordance with IFRS 15 'Revenue from Contracts with Customers'. The Company recognises revenue when (or as) it satisfies a performance obligation by transferring control of a promised good or service to a customer.</p>
<p>Revenue is measured at the transaction price, which is the amount of consideration to which the Company expects to be entitled in exchange for transferring promised goods or services, net of taxes and discounts.</p>""",

        DisclosureType.TAXATION: f"""<h3>Income Tax</h3>
<p>Income tax expense comprises current and deferred tax. Current tax is the expected tax payable on taxable income for the year, using tax rates enacted or substantively enacted at the reporting date.</p>
<p>Deferred tax is recognised in respect of temporary differences between the carrying amounts of assets and liabilities for financial reporting purposes and the amounts used for taxation purposes.</p>""",

        DisclosureType.SHARE_CAPITAL: f"""<p>The authorised and issued share capital of the Company is disclosed in the Statement of Changes in Equity.</p>
<p>Ordinary shares are classified as equity. Incremental costs directly attributable to the issue of ordinary shares are recognised as a deduction from equity, net of any tax effects.</p>""",

        DisclosureType.BORROWINGS: f"""<h3>Borrowings</h3>
<p>Borrowings are initially recognised at fair value, net of transaction costs incurred. Borrowings are subsequently measured at amortised cost using the effective interest method.</p>
<p>Borrowings are classified as current liabilities unless the Company has an unconditional right to defer settlement of the liability for at least 12 months after the reporting date.</p>""",

        DisclosureType.RELATED_PARTIES: f"""<h3>Related Party Transactions</h3>
<p>The Company has transactions with related parties, including key management personnel, directors and entities in which directors have a significant interest.</p>
<p>All related party transactions are conducted on an arm's length basis and on normal commercial terms. Key management compensation for the year is disclosed separately.</p>""",

        DisclosureType.COMMITMENTS: f"""<h3>Capital Commitments</h3>
<p>At {eng.period_end.strftime('%d %B %Y')}, the Company had no material capital commitments contracted for but not provided in the financial statements (prior year: nil).</p>

<h3>Operating Lease Commitments</h3>
<p>Future minimum lease payments under non-cancellable operating leases are disclosed in the note on Leases.</p>""",

        DisclosureType.EVENTS_AFTER_REPORTING: f"""<p>There are no events after the reporting date that would require adjustment to or disclosure in the financial statements.
</p>""",
    }

    return templates.get(dtype, f"<p>Disclosure note for {dtype.value} - please complete this note.</p>")


async def generate_disclosure_notes(
    eng_id: int,
    note_types: list[str] | None,
    regenerate_existing: bool,
    db: Session,
) -> list[DisclosureNote]:
    eng = db.query(Engagement).filter(Engagement.id == eng_id).first()
    if not eng:
        return []

    categories = _get_categories_in_use(eng_id, db)

    if note_types:
        types_to_generate = [DisclosureType(t) for t in note_types if t in DisclosureType.__members__]
    else:
        types_to_generate = [t for t in DISCLOSURE_ORDER if _disclosure_needed(t, categories)]

    if not regenerate_existing:
        existing_types = {n.note_type for n in db.query(DisclosureNote).filter(DisclosureNote.engagement_id == eng_id).all()}
        types_to_generate = [t for t in types_to_generate if t not in existing_types]

    results = []
    for order_idx, dtype in enumerate(types_to_generate, start=1):
        content = _generate_static_content(dtype, eng)

        # Try AI enhancement if OpenAI is configured
        from app.config import settings
        if settings.OPENAI_API_KEY:
            try:
                content = await _ai_enhance_disclosure(dtype, eng, content)
            except Exception:
                pass  # Fall back to template

        note = DisclosureNote(
            engagement_id=eng_id,
            note_type=dtype,
            note_number=order_idx,
            title=dtype.value.replace("_", " ").title(),
            content=content,
            is_ai_generated=True,
            order=order_idx,
        )
        db.add(note)
        results.append(note)

    db.commit()
    for n in results:
        db.refresh(n)
    return results


async def _ai_enhance_disclosure(dtype: DisclosureType, eng: Engagement, base_content: str) -> str:
    from app.services.openai_client import chat_completion
    prompt = f"""You are an IFRS expert. Enhance this financial statement disclosure note for {eng.client.name if eng.client else 'the Company'} (year ended {eng.period_end}).
Reporting standard: {eng.reporting_standard.value}
Currency: {eng.currency}

Disclosure type: {dtype.value}
Base content to enhance:
{base_content}

Improve the content to be more specific and professional while keeping it concise. Return only the HTML content, no extra text."""
    return await chat_completion([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=1500)
