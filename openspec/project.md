# Project Context

## Purpose
This is a serverless OCR (Optical Character Recognition) service that leverages the DeepSeek OCR model for high-quality text extraction and image understanding. The service is deployed on Modal.com and provides a REST API with multiple endpoints for different OCR tasks including image description, text location, and custom prompts.

## Tech Stack
- **Python 3.13**: Programming language (requires >=3.13)
- **Modal**: Serverless deployment platform for GPU-accelerated workloads
- **vLLM 0.11.0+**: Fast LLM inference engine with GPU optimization
- **FastAPI 0.120.0+**: Modern web framework for building APIs
- **PyTorch 2.8.0**: Deep learning framework
- **DeepSeek OCR**: Vision-language model for OCR tasks (deepseek-ai/DeepSeek-OCR)
- **CUDA 12.8.0**: NVIDIA GPU acceleration runtime
- **UV**: Fast Python package manager
- **Nix**: Development environment management (via flake.nix)
- **Pillow**: Image processing library
- **HuggingFace Hub**: Model distribution and caching

## Project Conventions

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Keep code concise and focused on performance
- Use snake_case for variables and functions
- Use environment variables for configuration (see env.py)
- Base64 encode images for API transfer
- Always verify tests actually work when writing them (per CLAUDE.md)

### Architecture Patterns
- **Serverless Functions**: Deploy on Modal with GPU allocation decorators
- **Provider Pattern**: Use a Provider class to share expensive model instances across requests
- **FastAPI Lifespan**: Initialize models during application startup, not per-request
- **Volume Mounting**: Cache HuggingFace models and vLLM artifacts in persistent volumes
- **Concurrent Processing**: Handle up to 3 concurrent inputs with `@modal.concurrent(max_inputs=3)`
- **GPU Optimization**: Use T4 GPUs for inference, with model-specific optimizations
- **Versioned API**: All endpoints use `/api/v1/*` pattern for future compatibility
- **Authentication**: Proxy authentication via Modal (requires_proxy_auth=True)

### Testing Strategy
- Manual integration testing via test.py script against deployed endpoints
- Environment-based configuration using MODAL_URL, MODAL_KEY, MODAL_SECRET
- Test with real image files (input.png, input1.png)
- Output verification by writing results to output.md
- **Critical**: Always verify tests actually work when writing them

### Git Workflow
- Main branch development (no feature branches currently)
- Conventional commit prefixes: `fix:`, `feat:`, optimization, etc.
- Keep commits focused and atomic
- Recent focus on deployment optimization and bug fixes

## Domain Context
- **OCR Tasks**: The service supports multiple OCR modalities:
  - **Describe**: Generate detailed descriptions of images
  - **Locate**: Find specific text within images and return bounding boxes
  - **Locate-Text**: Similar to locate but optimized for text queries
  - **Custom**: Accept custom prompts for flexible OCR tasks
- **Model Specifics**:
  - Uses pinned model revision (ee668a444ce026b7a23944f36692df1cdba54de9) for reproducibility
  - Employs N-gram logit processor for improved OCR quality
  - Disables prefix caching for this specific use case
  - Temperature 0.0 for deterministic outputs
  - Max tokens: 8192
  - Whitelists special tokens for table detection (<td>, </td>)

## Important Constraints
- **Python Version**: Requires Python 3.13+ (specified in pyproject.toml)
- **GPU Requirements**: Needs NVIDIA GPU for inference (currently uses T4)
- **Modal Deployment**: Application must be deployed to Modal.com infrastructure
- **Image Format**: Input images must be RGB PIL images
- **Model Size**: DeepSeek OCR is a large model requiring significant GPU memory
- **Cold Start**: Initial model loading takes time; FAST_BOOT flag used for optimization
- **Concurrency Limit**: Max 3 concurrent requests to manage GPU memory

## External Dependencies
- **Modal.com**: Serverless platform hosting the application
- **HuggingFace Hub**: Source for the DeepSeek OCR model weights
- **NVIDIA CUDA**: GPU runtime and drivers
- **vLLM Nightly Wheels**: Uses nightly build index for latest features
- **DeepSeek AI**: Model provider and repository maintainer
