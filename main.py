# main.py
from ocr_module import extract_text_from_image
from pipeline import analyze_contract
import json

if __name__ == "__main__":
    image_files = [
        "D:/25-2ocr2/page/page_1.png", 
        "D:/25-2ocr2/page/page_2.png",
        "D:/25-2ocr2/page/page_3.png",
        "D:/25-2ocr2/page/page_4.png"
    ]

    # 여러 페이지 OCR 결과를 합치기
    all_text = ""
    for image_path in image_files:
        text = extract_text_from_image(image_path)
        all_text += text + "\n"

    # 계약서 분석
    analysis = analyze_contract(all_text)

    # 결과 출력
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
