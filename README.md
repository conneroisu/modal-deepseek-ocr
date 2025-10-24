# Deepseek OCR Modal.com

This is a `modal.com` app that uses the [Deepseek OCR](https://github.com/deepseek/deepseek-ocr) model to perform OCR on images.

It uses vllm to perform inference, fastapi to serve the app, and modal to "host" the app.

## Installation (Using uv)

1. If uv is not installed, install it with `nix develop`
2. Install the app with `uv venv && uv sync`
3. Run the app with `modal deploy app.py`
4. DONE!
