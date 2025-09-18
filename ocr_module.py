import time
import requests
import uuid
import json

def run_ocr(image_file, api_url, secret_key):
    request_json = {
        'images': [{'format': 'jpg', 'name': 'demo'}],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }
    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    headers = {'X-OCR-SECRET': secret_key}

    with open(image_file, 'rb') as f:
        files = [('file', f)]
        response = requests.post(api_url, headers=headers, data=payload, files=files)

    if response.status_code != 200:
        raise RuntimeError(f"OCR 실패: {image_file}, 상태 코드 {response.status_code}")

    return response.json()
