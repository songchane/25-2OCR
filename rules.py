# rules.py
import re

# 위험 패턴 모음
RISK_PATTERNS = {
    "몰취": r"전액\s*몰취",
    "면책": r"면책",
    "위약금": r"위약금",
}

def apply_rules(clause: str) -> dict:
    """
    규칙 기반 위험 탐지
    """
    matches = []
    for name, pattern in RISK_PATTERNS.items():
        if re.search(pattern, clause):
            matches.append(name)
    return {"text": clause, "risk_matches": matches, "score": len(matches)}
