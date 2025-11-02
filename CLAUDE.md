# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## Project Overview

This is a Modal.com serverless application that serves OCR (Optical Character Recognition) using the DeepSeek-OCR model. It uses:
- **vLLM** for efficient LLM inference
- **FastAPI** for the HTTP API
- **Modal** for serverless deployment and GPU orchestration

## Development Setup

### Environment Setup
```bash
# Using Nix (recommended for reproducible environment)
nix develop

# Install dependencies with uv
uv venv && uv sync
```

### Deployment Commands
```bash
# Deploy the application to Modal
modal deploy app.py

# For development/testing (watch mode)
modal serve app.py
```

## Architecture

### Core Application (app.py)

The application is structured as a Modal serverless function with the following key components:

1. **Image Definition** (lines 3-24):
   - Base: NVIDIA CUDA 12.8.0 on Ubuntu 22.04
   - Python 3.12 runtime
   - Custom dependency installation using uv for torch and related packages
   - vLLM installed from nightly wheels
   - Optimized for HuggingFace model transfers with `HF_HUB_ENABLE_HF_TRANSFER`

2. **Model Configuration** (lines 32-35):
   - Model: `deepseek-ai/DeepSeek-OCR`
   - Pinned revision: `ee668a444ce026b7a23944f36692df1cdba54de9` (prevents unexpected model updates)
   - GPU: T4 (configurable via `GPU` constant)
   - Concurrent requests: max 3 (`@modal.concurrent(max_inputs=3)`)

3. **vLLM Setup** (lines 55-72):
   - Uses NGramPerReqLogitsProcessor for better OCR output
   - Prefix caching disabled
   - Temperature: 0.0 (deterministic)
   - Max tokens: 8192
   - Special token whitelist: `{128821, 128822}` for table tags `<td>`, `</td>`

4. **API Endpoints**:
   - All endpoints accept base64-encoded images
   - `/api/v1/describe`: General image description
   - `/api/v1/locate`: Locate specific text in image (returns coordinates)
   - `/api/v1/locate-text`: Same as locate (redundant endpoint)
   - `/api/v1/custom`: Custom prompt with image

### Authentication
The API requires Modal proxy authentication (`@modal.asgi_app(requires_proxy_auth=True)`). Clients must provide:
- `Modal-Key` header
- `Modal-Secret` header

See test.py for authentication example.

### Testing

**test.py**: Simple client that calls the deployed Modal endpoint. Requires environment variables:
```bash
export MODAL_URL="https://your-username--modal-deepseek-ocr-ocrapp.modal.run/api/v1/describe"
export MODAL_KEY="your-modal-key"
export MODAL_SECRET="your-modal-secret"
```

**env.py**: Development test script with hardcoded credentials (⚠️ contains exposed credentials - do not commit changes to this file).

## Code Quality

### Formatting
```bash
# Format Python code (run before committing)
nix fmt
# or individually:
black *.py
isort *.py
ruff --fix *.py
```

### Type Checking
```bash
basedpyright *.py
# or
mypy *.py
```

## Important Notes

- **Model Version Pinning**: The model revision is pinned to prevent breaking changes from upstream model updates
- **GPU Selection**: Currently uses T4 GPUs. Modify the `GPU` constant for different GPU types
- **Concurrent Requests**: Limited to 3 concurrent inputs. Adjust `@modal.concurrent(max_inputs=3)` if needed
- **Image Processing**: All images are temporarily written to disk, converted to RGB, then processed. Files are not cleaned up automatically
- **Authentication**: The application uses Modal's built-in proxy authentication. Generate credentials via Modal dashboard
- **Python Version**: The container uses Python 3.12, but local development uses Python 3.13 (per pyproject.toml)

## Modal-Specific Patterns

- **Volumes**: Two Modal volumes are defined but not currently mounted:
  - `huggingface-cache`: For caching downloaded models
  - `vllm-cache`: For vLLM compilation cache
- **ASGI App**: The FastAPI app is wrapped with `@modal.asgi_app()` to create an HTTP endpoint
- **Lifespan Management**: Model loading happens in FastAPI lifespan context (lines 55-75), ensuring the model is loaded once per container

## Common Development Tasks

### Changing the Model
1. Update `MODEL_NAME` and optionally `MODEL_REVISION` in app.py
2. Verify the model is compatible with vLLM's multimodal support
3. Adjust `SamplingParams` if needed for the new model
4. Test with `modal serve app.py` before deploying

### Adding New Endpoints
1. Add endpoint function inside the `ocrapp()` function after line 173
2. Use the same pattern: accept `Request`, decode base64 image, process with `provider.llm.generate()`
3. Return JSON with `{"output": text}`

### Modifying Inference Parameters
Edit the `SamplingParams` instantiation (lines 63-72):
- `temperature`: Control randomness (0.0 = deterministic)
- `max_tokens`: Maximum output length
- `extra_args`: NGram processor settings for table extraction

### Testing Changes Locally
```bash
# Serve locally (hot-reload on changes)
modal serve app.py

# Test with curl or test.py
python test.py
```
