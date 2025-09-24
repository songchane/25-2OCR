from ocr_module import run_ocr
from segmentation import extract_texts
from analyzer import extract_special_clauses, tag_entities
from embedding_match import embed_and_match

def clean_text(text: str) -> str:
    replacements = {
        "�": "·",
        "ㆍ": "·",
        "∙": "·",
        "•": "·",
        "．": ".",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


# def process_documents(image_files, api_url, secret_key,
#                       good_examples=None, bad_examples=None):
#     all_texts = []
#     for image_file in image_files:
#         ocr_results = run_ocr(image_file, api_url, secret_key)
#         texts = extract_texts(ocr_results)
#         texts = [clean_text(t) for t in texts]
#         all_texts.extend(texts)

#     full_text = "\n".join(all_texts)
#     clauses = extract_special_clauses(full_text)

#     skip_sentence = (
#         "본 계약을 증명하기 위하여 계약 당사자가 이의 없음을 확인하고 "
#         "각각 서명․날인 후 임대인, 임차인, 개업공인중개사는 매 장마다 간인하여, "
#         "각각 1통씩 보관한다."
#     )
#     clauses = [c for c in clauses if c.strip() != skip_sentence.strip()]

#     enriched_clauses = []
#     for c in clauses:
#         entities = tag_entities(c)
#         enriched_clauses.append({
#             "clause": c,
#             "entities": entities
#         })

#     matched = embed_and_match(clauses,
#                               good_examples=good_examples,
#                               bad_examples=bad_examples)
#     return {"clauses": enriched_clauses, "embedding_match": matched}

def process_documents(image_files, api_url, secret_key,
                      good_examples=None, bad_examples=None):
    all_texts = []
    for image_file in image_files:
        ocr_results = run_ocr(image_file, api_url, secret_key)
        texts = extract_texts(ocr_results)
        texts = [clean_text(t) for t in texts]
        all_texts.extend(texts)

    # 문장 단위 조항 분리
    full_text = "\n".join(all_texts)
    clauses = extract_special_clauses(full_text)

    # 특정 문장은 제외
    skip_sentence = (
        "본 계약을 증명하기 위하여 계약 당사자가 이의 없음을 확인하고 "
        "각각 서명․날인 후 임대인, 임차인, 개업공인중개사는 매 장마다 간인하여, "
        "각각 1통씩 보관한다."
    )
    clauses = [c for c in clauses if c.strip() != skip_sentence.strip()]

    # 엔티티 태깅 (숫자/날짜만)
    enriched_clauses = []
    for c in clauses:
        entities = tag_entities(c)
        enriched_clauses.append({
            "clause": c,
            "entities": entities
        })

    # 좋은/나쁜 예시 기반 유사도 평가
    matched = embed_and_match(
        clauses,
        good_examples=good_examples,
        bad_examples=bad_examples
    )

    return {
        "clauses": enriched_clauses,
        "embedding_match": matched
    }
