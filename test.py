import requests
import base64
from os import environ

# url = "https://{usr}--modal-deepseek-ocr-ocrapp.modal.run/api/v1/describe"
url = environ.get("MODAL_URL")
if url is None:
    raise Exception("MODAL_URL not set")
modal_key = environ.get("MODAL_KEY")
if modal_key is None:
    raise Exception("MODAL_KEY not set")
model_secret = environ.get("MODAL_SECRET")
if model_secret is None:
    raise Exception("MODAL_SECRET not set")

data = {
    "file_name": "input.png",
    "image": base64.b64encode(open('./input.png', 'rb').read()).decode('utf-8')
}

response = requests.post(
    url,
    json=data,
    headers={
    "Modal-Key": modal_key,
    "Modal-Secret": model_secret,
    })

with open('output.md', 'w') as f:
    f.write(response.json()['output'])

print("Response:")
print(response.json())
