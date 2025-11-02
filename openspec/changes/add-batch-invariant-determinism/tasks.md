# Implementation Tasks

## 1. Dependency Installation
- [ ] 1.1 Add git clone and pip install of `batch_invariant_ops` to Modal container image (use `git+https://github.com/thinking-machines-lab/batch_invariant_ops.git`)
- [ ] 1.2 Add `batch_invariant_ops` to pyproject.toml dependencies using git URL for local development
- [ ] 1.3 Verify the library installs correctly in the CUDA 12.8 + PyTorch 2.8 environment

## 2. Code Integration
- [ ] 2.1 Import `set_batch_invariant_mode` in the ocrapp function
- [ ] 2.2 Wrap vLLM model initialization with `set_batch_invariant_mode()` context manager
- [ ] 2.3 Ensure the context manager scope covers all model inference calls

## 3. Testing & Validation
- [ ] 3.1 Create test script to verify determinism across different batch sizes
- [ ] 3.2 Run test with same image at batch sizes 1, 2, 3 and verify identical outputs
- [ ] 3.3 Document any performance impact from batch-invariant operations

## 4. Documentation
- [ ] 4.1 Update CLAUDE.md with batch-invariant operations information
- [ ] 4.2 Add comments in code explaining the determinism guarantee
- [ ] 4.3 Note any trade-offs (e.g., minor performance overhead) in documentation
