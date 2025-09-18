# llm_judge.py
import openai

def judge_with_llm(clause: str, rules_result: dict, embedding_result: list) -> dict:
    """
    규칙·임베딩 결과를 LLM에 전달해 최종 판정 및 수정안 생성
    """
    prompt = f"""
    계약 조항: {clause}
    규칙 기반 결과: {rules_result}
    임베딩 결과: {embedding_result}

    이 조항의 위험성을 평가하고, 필요 시 수정안을 제안해 주세요.
    """
    # TODO: 실제 GPT API 연동
    return {"judgement": "위험함", "suggestion": "위약금 전액 몰취 대신 합리적 배상액으로 수정"}
