from typing import List, Set
from sqlalchemy.orm import Session
from models.naics_models import Sector, IndustryGroup, Industry, SubIndustry
from rapidfuzz import fuzz

def highlight_keyword(text: str, keyword: str) -> str:
    if not keyword:
        return text
    keyword_lower = keyword.lower()
    if keyword_lower in text.lower():
        index = text.lower().index(keyword_lower)
        return (
            text[:index] +
            f"<span style='background-color: #ffff66'><b>{text[index:index+len(keyword)]}</b></span>" +
            text[index+len(keyword):]
        )
    return text

def search_naics_hierarchy(session: Session, keyword: str) -> List[Sector]:
    """
    Smart search with All Keywords → Partial → Fuzzy.
    Returns sectors that match any level.
    """
    keyword = keyword.strip()
    if not keyword:
        return session.query(Sector).all()

    words = keyword.split()
    matching_sectors: Set[Sector] = set()

    # === 1. All Keywords Match ===
    def match_all_keywords(queryset, field_getter):
        q = queryset
        for word in words:
            q = q.filter(field_getter().ilike(f"%{word}%"))
        return q.all()

    subs = match_all_keywords(session.query(SubIndustry), lambda: SubIndustry.name)
    for sub in subs:
        sub.name = highlight_keyword(sub.name, keyword)
        if sub.industry:
            matching_sectors.add(sub.industry.industry_group.sector)

    inds = match_all_keywords(session.query(Industry), lambda: Industry.name)
    for ind in inds:
        ind.name = highlight_keyword(ind.name, keyword)
        matching_sectors.add(ind.industry_group.sector)

    igs = match_all_keywords(session.query(IndustryGroup), lambda: IndustryGroup.name)
    for ig in igs:
        ig.name = highlight_keyword(ig.name, keyword)
        matching_sectors.add(ig.sector)

    secs = match_all_keywords(session.query(Sector), lambda: Sector.name)
    for sec in secs:
        sec.name = highlight_keyword(sec.name, keyword)
        matching_sectors.add(sec)

    # === 2. Fallback: Partial Match ===
    if not matching_sectors:
        partial_query = f"%{keyword}%"

        subs = session.query(SubIndustry).filter(SubIndustry.name.ilike(partial_query)).all()
        for sub in subs:
            sub.name = highlight_keyword(sub.name, keyword)
            if sub.industry:
                matching_sectors.add(sub.industry.industry_group.sector)

        inds = session.query(Industry).filter(Industry.name.ilike(partial_query)).all()
        for ind in inds:
            ind.name = highlight_keyword(ind.name, keyword)
            matching_sectors.add(ind.industry_group.sector)

        igs = session.query(IndustryGroup).filter(IndustryGroup.name.ilike(partial_query)).all()
        for ig in igs:
            ig.name = highlight_keyword(ig.name, keyword)
            matching_sectors.add(ig.sector)

        secs = session.query(Sector).filter(Sector.name.ilike(partial_query)).all()
        for sec in secs:
            sec.name = highlight_keyword(sec.name, keyword)
            matching_sectors.add(sec)

    # === 3. Fallback: Fuzzy Match ===
    if not matching_sectors:
        all_subs = session.query(SubIndustry).all()
        all_inds = session.query(Industry).all()
        all_igs = session.query(IndustryGroup).all()
        all_secs = session.query(Sector).all()

        def fuzzy_top_matches(items, name_attr):
            scored = [(item, fuzz.partial_ratio(keyword.lower(), getattr(item, name_attr).lower())) for item in items]
            return [i for i, score in sorted(scored, key=lambda x: x[1], reverse=True) if score > 80][:10]

        for sub in fuzzy_top_matches(all_subs, "name"):
            sub.name = highlight_keyword(sub.name, keyword)
            if sub.industry:
                matching_sectors.add(sub.industry.industry_group.sector)

        for ind in fuzzy_top_matches(all_inds, "name"):
            ind.name = highlight_keyword(ind.name, keyword)
            matching_sectors.add(ind.industry_group.sector)

        for ig in fuzzy_top_matches(all_igs, "name"):
            ig.name = highlight_keyword(ig.name, keyword)
            matching_sectors.add(ig.sector)

        for sec in fuzzy_top_matches(all_secs, "name"):
            sec.name = highlight_keyword(sec.name, keyword)
            matching_sectors.add(sec)

    return list(matching_sectors)