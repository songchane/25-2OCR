from sentence_transformers import SentenceTransformer, util
import numpy as np

# ✅ 사전 학습된 임베딩 모델
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_and_match(clauses, good_examples=None, bad_examples=None, risk_keywords=None):
    """
    clauses: 분석할 조항 리스트
    good_examples: 안전한 문장 리스트
    bad_examples: 위험한 문장 리스트
    risk_keywords: 위험 키워드 리스트
    """
    results = []

    # ===== 예시 임베딩 =====
    good_emb = model.encode(good_examples, convert_to_tensor=True) if good_examples else None
    bad_emb = model.encode(bad_examples, convert_to_tensor=True) if bad_examples else None

    # ✅ 프로토타입(센터로이드)
    good_proto = good_emb.mean(dim=0) if good_emb is not None else None
    bad_proto = bad_emb.mean(dim=0) if bad_emb is not None else None

    final_scores = []

    for c in clauses:
        clause_emb = model.encode(c, convert_to_tensor=True)

        # ---- Good 예시 ----
        good_sim = 0.0
        good_topk = 0.0
        good_proto_sim = 0.0
        if good_emb is not None:
            sims = util.cos_sim(clause_emb, good_emb)[0].cpu().numpy()
            good_sim = float(sims.max())
            good_topk = float(np.mean(sorted(sims, reverse=True)[:3]))
            if good_proto is not None:
                good_proto_sim = float(util.cos_sim(clause_emb, good_proto)[0][0])

        # ---- Bad 예시 ----
        bad_sim = 0.0
        bad_topk = 0.0
        bad_proto_sim = 0.0
        if bad_emb is not None:
            sims = util.cos_sim(clause_emb, bad_emb)[0].cpu().numpy()
            bad_sim = float(sims.max())
            bad_topk = float(np.mean(sorted(sims, reverse=True)[:3]))
            if bad_proto is not None:
                bad_proto_sim = float(util.cos_sim(clause_emb, bad_proto)[0][0])

        # ---- 종합 점수 ----
        score_max = good_sim - bad_sim
        score_topk = good_topk - bad_topk
        score_proto = good_proto_sim - bad_proto_sim

        final_score = 0.4 * score_max + 0.4 * score_topk + 0.2 * score_proto

        # ---- 규칙 보정: 위험 키워드 ----
        penalty = 0.0
        if risk_keywords:
            for kw in risk_keywords:
                if kw in c:
                    penalty -= 0.1
        final_score += penalty

        final_scores.append(final_score)

        results.append({
            "clause": c,
            "good_sim": round(good_sim, 3),
            "bad_sim": round(bad_sim, 3),
            "final_score": round(final_score, 3),  # 보정 포함
            "grade_text": None  # 나중에 채움
        })

    # ===== 동적 기준 적용 =====
    if final_scores:
        scores = np.array(final_scores)
        mean, std = scores.mean(), scores.std()

        low_th = mean - 0.5 * std
        high_th = mean + 0.5 * std

        for r in results:
            fs = r["final_score"]

            # 절대 트리거 우선
            if r["bad_sim"] >= 0.85:
                r["grade_text"] = "위험"
            elif r["good_sim"] >= 0.85 and r["bad_sim"] <= 0.6:
                r["grade_text"] = "안전"
            else:
                # 동적 기준
                if fs <= low_th:
                    r["grade_text"] = "위험"
                elif fs >= high_th:
                    r["grade_text"] = "안전"
                else:
                    r["grade_text"] = "경고"

    return results
