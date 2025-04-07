#naics_search_utils.py

from typing import List
from sqlalchemy.orm import Session
from models.naics_models import SubIndustry
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

def search_naics_hierarchy(session: Session, q: str) -> List[dict]:
    """
    Smart search:
    1. Try All Keywords Match
    2. If empty, try Partial Match
    3. If still empty, try Fuzzy Match
    """
    q = q.strip()
    if not q:
        return []

    # 1. All keywords match
    words = q.split()
    query = session.query(SubIndustry)
    for word in words:
        query = query.filter(SubIndustry.name.ilike(f"%{word}%"))
    results = query.all()

    if results:
        return [{"code": r.code, "name": highlight_keyword(r.name, q)} for r in results]

    # 2. Partial match
    results = session.query(SubIndustry).filter(SubIndustry.name.ilike(f"%{q}%")).all()
    if results:
        return [{"code": r.code, "name": highlight_keyword(r.name, q)} for r in results]

    # 3. Fuzzy match
    all_rows = session.query(SubIndustry).all()
    scored = [(r, fuzz.partial_ratio(q.lower(), r.name.lower())) for r in all_rows]
    results = [r for r, score in sorted(scored, key=lambda x: x[1], reverse=True) if score > 80][:10]
    return [{"code": r.code, "name": highlight_keyword(r.name, q)} for r in results]