import requests
import uuid
import time
import json
import os

def extract_text_from_image(image_path: str) -> str:
    api_url = "https://sue3ozo9cm.apigw.ntruss.com/custom/v1/46155/8d01cdf5a18c9bd7d11f57df503df86a6a4a7a21309a2a4a1ca688c1e8e36085/infer"
    secret_key = "ZkpndlpSTWxRektUQkZ2Z05nUUxoTGJhem1GSk9CUFU="

    # 🔽 파일 확장자 자동 추출 (소문자로 변환)
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext not in ["png", "jpg", "jpeg"]:
        raise ValueError(f"지원하지 않는 이미지 형식입니다: {ext}")

    request_json = {
        "images": [
            {
                "format": ext,      # 자동으로 png/jpg/jpeg 맞춰 넣음
                "name": "contract_page"
            }
        ],
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": int(round(time.time() * 1000))
    }

    payload = {"message": json.dumps(request_json).encode("utf-8")}
    files = [("file", open(image_path, "rb"))]
    headers = {"X-OCR-SECRET": secret_key}

    response = requests.post(api_url, headers=headers, data=payload, files=files)
    result = response.json()

    print("OCR Response:", result)  # 🔍 디버깅용

    if "images" not in result:
        raise ValueError(f"OCR 실패: {result}")

    # 텍스트 추출
    text = "\n".join([f["inferText"] for f in result["images"][0]["fields"]])
    return text
