def extract_texts(ocr_results):
    texts = []
    for image_result in ocr_results.get('images', []):
        for field in image_result.get('fields', []):
            text = field.get('inferText', '')
            if text:
                texts.append(text)
    return texts
