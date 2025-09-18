# normalize.py
import re

def normalize_clause(clause: str) -> dict:
    """
    금액, 날짜, %, 기간 등을 태깅하여 전처리
    """
    normalized = clause
    tags = {
        "money": re.findall(r"\d+(?:,\d{3})*원", clause),
        "percent": re.findall(r"\d+%", clause),
        "date": re.findall(r"\d{4}[./-]\d{1,2}[./-]\d{1,2}", clause),
        "roles": re.findall(r"(임대인|임차인)", clause),
    }
    return {"text": normalized, "tags": tags}
