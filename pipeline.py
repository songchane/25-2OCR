# pipeline.py
from ocr_module import extract_text_from_image
from segmentation import segment_contract
from normalize import normalize_clause
from rules import apply_rules
from embedding_match import find_similar_examples
from llm_judge import judge_with_llm

def analyze_contract(text: str) -> dict:
    """
    전체 계약서 분석 파이프라인
    """
    results = []
    clauses = segment_contract(text)

    for clause in clauses:
        norm = normalize_clause(clause)
        rule_res = apply_rules(clause)
        embed_res = find_similar_examples(clause)
        llm_res = judge_with_llm(clause, rule_res, embed_res)

        results.append({
            "original": clause,
            "normalized": norm,
            "rules": rule_res,
            "embedding": embed_res,
            "llm": llm_res
        })
    return {"clauses": results}
