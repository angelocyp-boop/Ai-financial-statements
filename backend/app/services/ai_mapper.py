"""AI-powered account mapper: combines library lookup + GPT classification."""
from __future__ import annotations
import asyncio
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.trial_balance import TrialBalance, TBLine
from app.models.mapping import MappingLibrary, IFRSCategory
from app.services.ifrs_taxonomy import MAPPING_HINTS


def _library_match(name: str, code: str | None, library: list[MappingLibrary]) -> MappingLibrary | None:
    name_lower = name.lower()
    for entry in library:
        if entry.account_code_pattern and code:
            if code.startswith(entry.account_code_pattern.rstrip("*")):
                return entry
        if entry.account_name_keywords:
            if any(kw.lower() in name_lower for kw in entry.account_name_keywords):
                return entry
    return None


def _keyword_match(name: str) -> tuple[str | None, float]:
    name_lower = name.lower()
    best_category = None
    best_score = 0.0
    for category, keywords in MAPPING_HINTS.items():
        matches = sum(1 for kw in keywords if kw in name_lower)
        if matches > 0:
            score = matches / len(keywords)
            if score > best_score:
                best_score = score
                best_category = category
    return best_category, min(0.85, best_score * 3)


async def run_bulk_mapping(tb_id: int, firm_id: int, db: Session | None) -> None:
    from app.database import SessionLocal
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False

    try:
        tb = db.query(TrialBalance).filter(TrialBalance.id == tb_id).first()
        if not tb:
            return

        lines = db.query(TBLine).filter(
            TBLine.trial_balance_id == tb_id,
            TBLine.ifrs_category == None,
            TBLine.is_manually_mapped == False,
        ).all()

        library = db.query(MappingLibrary).filter(MappingLibrary.firm_id == firm_id).all()

        # Phase 1: library + keyword matching (instant)
        unmatched_ids = []
        for line in lines:
            lib_match = _library_match(line.account_name, line.account_code, library)
            if lib_match:
                line.ifrs_category = lib_match.ifrs_category.value
                line.mapping_confidence = Decimal("0.95")
                line.mapping_explanation = f"Matched from firm mapping library (used {lib_match.usage_count}x)"
                lib_match.usage_count += 1
            else:
                kw_cat, kw_score = _keyword_match(line.account_name)
                if kw_cat and kw_score >= 0.4:
                    line.ifrs_category = kw_cat
                    line.mapping_confidence = Decimal(str(round(kw_score, 4)))
                    line.mapping_explanation = f"Keyword match: '{kw_cat}'"
                else:
                    unmatched_ids.append(line.id)

        db.flush()

        # Phase 2: AI classification for unmatched lines
        if unmatched_ids:
            from app.config import settings
            if settings.OPENAI_API_KEY:
                from app.services.openai_client import classify_accounts_batch
                unmatched_lines = db.query(TBLine).filter(TBLine.id.in_(unmatched_ids)).all()
                batch_size = 40
                for i in range(0, len(unmatched_lines), batch_size):
                    batch = unmatched_lines[i:i + batch_size]
                    accounts = [{"id": l.id, "code": l.account_code, "name": l.account_name} for l in batch]
                    classifications = await classify_accounts_batch(accounts)
                    cls_map = {c["id"]: c for c in classifications if "id" in c}
                    for line in batch:
                        if line.id in cls_map:
                            cls = cls_map[line.id]
                            try:
                                IFRSCategory(cls["category"])
                                line.ifrs_category = cls["category"]
                                line.mapping_confidence = Decimal(str(round(float(cls.get("confidence", 0.7)), 4)))
                                line.mapping_explanation = cls.get("explanation", "AI classified")
                                line.normal_balance = cls.get("normal_balance", "DR")
                            except ValueError:
                                pass
            else:
                # Fallback: assign best keyword match or OTHER_NC_ASSETS
                for line_id in unmatched_ids:
                    line = next((l for l in lines if l.id == line_id), None)
                    if line and not line.ifrs_category:
                        line.ifrs_category = "OTHER_NC_ASSETS"
                        line.mapping_confidence = Decimal("0.2")
                        line.mapping_explanation = "Could not classify - please review"

        # Update mapped count
        mapped = sum(1 for l in lines if l.ifrs_category)
        tb.mapped_count = mapped
        db.commit()

        # Learn from high-confidence mappings into firm library
        for line in lines:
            if line.ifrs_category and line.mapping_confidence and line.mapping_confidence >= Decimal("0.8") and not line.is_manually_mapped:
                existing = _library_match(line.account_name, line.account_code, library)
                if not existing:
                    words = [w for w in line.account_name.lower().split() if len(w) > 3]
                    if words:
                        new_entry = MappingLibrary(
                            firm_id=firm_id,
                            account_code_pattern=line.account_code[:3] if line.account_code else None,
                            account_name_keywords=words[:5],
                            ifrs_category=IFRSCategory(line.ifrs_category),
                            normal_balance=line.normal_balance or "DR",
                        )
                        db.add(new_entry)
        db.commit()

    finally:
        if should_close:
            db.close()
