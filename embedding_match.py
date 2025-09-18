# embedding_match.py
from typing import List

def find_similar_examples(clause: str) -> List[dict]:
    """
    예시 문장 임베딩 기반 유사도 검색 (FAISS/pgvector 연동)
    """
    # TODO: 벡터화 & 검색 로직 연결
    return [
        {"example": "보증금 전액 몰취 조항", "similarity": 0.89, "label": "bad"},
        {"example": "임대인과 임차인은 협의하여 조정한다", "similarity": 0.75, "label": "good"},
    ]
