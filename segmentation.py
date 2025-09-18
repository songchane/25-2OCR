# segmentation.py
import re

def segment_contract(text: str) -> list[str]:
    """
    계약서 텍스트를 조항 단위로 분리
    """
    # "제1조", "제2조" 같은 패턴 기준 분리
    clauses = re.split(r"(제\d+조.*)", text)
    # 빈 항목 제거 및 클린업
    return [c.strip() for c in clauses if c.strip()]
