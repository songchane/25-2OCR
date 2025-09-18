from ocr_module import run_ocr
from segmentation import extract_texts
from analyzer import extract_special_clauses, tag_entities, match_risk_keywords
from embedding_match import embed_and_match

def process_documents(image_files, api_url, secret_key, risk_keywords=None, example_db=None):
    all_texts = []

    for image_file in image_files:
        ocr_results = run_ocr(image_file, api_url, secret_key)
        texts = extract_texts(ocr_results)
        all_texts.extend(texts)

    full_text = "\n".join(all_texts)
    clauses = extract_special_clauses(full_text)

    enriched_clauses = []
    for c in clauses:
        entities = tag_entities(c)
        risk = match_risk_keywords(c, risk_keywords or [])
        enriched_clauses.append({"clause": c, "entities": entities, "risk": risk})

    matched = embed_and_match(clauses, example_db=example_db)
    return {"clauses": enriched_clauses, "embedding_match": matched}
