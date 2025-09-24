from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_and_match(clauses, good_examples=None, bad_examples=None):
    """
    clauses: 분석 대상 문장 리스트
    good_examples: 안전한 문장 리스트
    bad_examples: 위험한 문장 리스트
    """
    results = []

    # 미리 임베딩
    good_emb = model.encode(good_examples, convert_to_tensor=True) if good_examples else None
    bad_emb = model.encode(bad_examples, convert_to_tensor=True) if bad_examples else None

    for c in clauses:
        clause_emb = model.encode(c, convert_to_tensor=True)

        # 좋은 예시와의 유사도
        good_sim = 0.0
        if good_emb is not None:
            sims = util.cos_sim(clause_emb, good_emb)[0]
            good_sim = float(sims.max())

        # 나쁜 예시와의 유사도
        bad_sim = 0.0
        if bad_emb is not None:
            sims = util.cos_sim(clause_emb, bad_emb)[0]
            bad_sim = float(sims.max())

        # FinalScore = 좋은 예시와 가까울수록 ↑, 나쁜 예시와 가까울수록 ↓
        final_score = good_sim - bad_sim

        # 등급 판정
        if final_score < -0.2:
            grade = "위험"
        elif final_score < 0.2:
            grade = "경고"
        else:
            grade = "안전"

        results.append({
            "clause": c,
            "good_sim": round(good_sim, 3),
            "bad_sim": round(bad_sim, 3),
            "final_score": round(final_score, 3),
            "grade_text": grade
        })

    return results
