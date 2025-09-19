# from pipeline import process_documents

# if __name__ == "__main__":
#     secret_key = 'WXJaUVdTdU9QREVHZnZrTnpQRWt0TlFGVHZvS3dPQkk='
#     api_url = 'https://sue3ozo9cm.apigw.ntruss.com/custom/v1/46163/76ed309608501247a724d594f79abff5f798666c3c204556ddd144ad99a6a553/general'

#     image_files = [
#         "D:/25-2ocr2/page/page_1.png",
#         "D:/25-2ocr2/page/page_2.png",
#         "D:/25-2ocr2/page/page_3.png",
#         "D:/25-2ocr2/page/page_4.png"
#     ]

#     risk_keywords = ["위약금", "손해배상", "강제", "의무"]
#     example_db = ["예시 조항1", "예시 조항2"]

#     results = process_documents(image_files, api_url, secret_key, risk_keywords, example_db)

#     print("=== 최종 분석 결과 ===")
#     for r in results["clauses"]:
#         print(r)

#     print("\n=== 유사 임베딩 매칭 결과 ===")
#     for m in results["embedding_match"]:
#         print(m)

import os
from dotenv import load_dotenv
from pipeline import process_documents

if __name__ == "__main__":
    # .env 파일 로드
    load_dotenv()

    api_url = os.getenv("API_URL")
    secret_key = os.getenv("SECRET_KEY")
    image_dir = os.getenv("IMAGE_DIR")

    # IMAGE_DIR 안의 png/jpg/jpeg 파일 자동 수집
    valid_ext = (".png", ".jpg", ".jpeg")
    image_files = [
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if f.lower().endswith(valid_ext)
    ]

    risk_keywords = ["위약금", "손해배상", "강제", "의무"]
    example_db = ["예시 조항1", "예시 조항2"]

    results = process_documents(image_files, api_url, secret_key, risk_keywords, example_db)

    print("=== 최종 분석 결과 ===")
    for r in results["clauses"]:
        print(r)

    print("\n=== 유사 임베딩 매칭 결과 ===")
    for m in results["embedding_match"]:
        print(m)
