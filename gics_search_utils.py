from typing import List, Set
from sqlalchemy.orm import Session
from models.models import Sector, IndustryGroup, Industry, SubIndustry

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

def search_gics_hierarchy(session: Session, keyword: str) -> List[Sector]:
    """
    Search all GICS levels and return a list of matching sectors.
    Highlights keyword in names (HTML-safe).
    """
    keyword = keyword.strip()
    if not keyword:
        return session.query(Sector).all()

    query = f"%{keyword}%"
    matching_sectors: Set[Sector] = set()

    subs = session.query(SubIndustry).filter(SubIndustry.name.ilike(query)).all()
    for sub in subs:
        sub.name = highlight_keyword(sub.name, keyword)
        if sub.industry:
            matching_sectors.add(sub.industry.industry_group.sector)

    inds = session.query(Industry).filter(Industry.name.ilike(query)).all()
    for ind in inds:
        ind.name = highlight_keyword(ind.name, keyword)
        matching_sectors.add(ind.industry_group.sector)

    igs = session.query(IndustryGroup).filter(IndustryGroup.name.ilike(query)).all()
    for ig in igs:
        ig.name = highlight_keyword(ig.name, keyword)
        matching_sectors.add(ig.sector)

    secs = session.query(Sector).filter(Sector.name.ilike(query)).all()
    for sec in secs:
        sec.name = highlight_keyword(sec.name, keyword)
        matching_sectors.add(sec)

    return list(matching_sectors)
