# Add Batch-Invariant Determinism

## Why

The current implementation uses `temperature=0.0` in vLLM's SamplingParams to achieve deterministic outputs, but this only controls sampling behavior at the decoding level. PyTorch operations within the model itself (matrix multiplications, softmax, reductions) can still produce non-deterministic results due to batch size variations, parallel execution order, and hardware-specific optimizations. This creates reproducibility issues where the same input with different batching strategies can produce different OCR outputs.

The `batch_invariant_ops` library solves this by replacing standard PyTorch kernels with batch-invariant implementations that guarantee identical results regardless of batch size or execution order.

## What Changes

- **Add** `batch_invariant_ops` as a dependency to the Modal container image
- **Wrap** vLLM model initialization with `set_batch_invariant_mode()` context manager
- **Update** inference code to enable batch-invariant operations during generation
- **Document** the determinism guarantees and trade-offs

## Impact

- **Affected specs**: `ocr-inference` (new capability spec)
- **Affected code**:
  - `app.py:3-24` - Container image dependency installation
  - `app.py:55-75` - FastAPI lifespan and model initialization
  - `pyproject.toml:7-12` - Development dependencies
- **Performance**: Minor overhead from batch-invariant kernel substitutions
- **Compatibility**: No breaking changes to API endpoints or response formats
- **Reproducibility**: Improved - same inputs now guaranteed to produce identical outputs across different batch sizes
