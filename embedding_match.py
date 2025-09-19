# def embed_and_match(clauses, example_db=None):
#     """
#     임베딩 기반 매칭 (샘플 구현)
#     """
#     if not example_db:
#         return [{"clause": c, "similar_to": None} for c in clauses]

#     results = []
#     for c in clauses:
#         # TODO: 실제 벡터 임베딩 + 코사인 유사도 검색 구현
#         matched = example_db[0] if example_db else None
#         results.append({"clause": c, "similar_to": matched})
#     return results

from sentence_transformers import SentenceTransformer, util

from sentence_transformers import SentenceTransformer, util

# 사전 학습된 임베딩 모델 로드 (최초 실행 시 다운로드 후 캐시에 저장됨)
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_and_match(clauses, example_db=None, top_k=1):
    """
    조항(clauses)과 예시 DB(example_db)를 임베딩 후 유사도 매칭
    - clauses: 분석 대상 문장 리스트
    - example_db: 비교할 예시 문장 리스트
    - top_k: 가장 유사한 문장 몇 개까지 반환할지 (기본 1개)

    return: [{clause, matches:[{text, similarity}, ...]}]
    """
    if not example_db:
        return [{"clause": c, "matches": []} for c in clauses]

    # 예시 DB 임베딩
    db_embeddings = model.encode(example_db, convert_to_tensor=True)

    results = []
    for c in clauses:
        # 조항 임베딩
        clause_embedding = model.encode(c, convert_to_tensor=True)

        # 코사인 유사도 계산
        cos_scores = util.cos_sim(clause_embedding, db_embeddings)[0]

        # top_k 유사 문장 뽑기
        top_results = cos_scores.topk(k=min(top_k, len(example_db)))

        matches = []
        for score, idx in zip(top_results[0], top_results[1]):
            matches.append({
                "text": example_db[int(idx)],
                "similarity": round(float(score), 3)
            })

        results.append({
            "clause": c,
            "matches": matches
        })

    return results

