# OCR Inference Specification

## ADDED Requirements

### Requirement: Batch-Invariant Deterministic Inference
The OCR service SHALL produce identical outputs for the same input image regardless of batch size or concurrent request patterns.

#### Scenario: Same input produces identical output across different batch sizes
- **GIVEN** an input image encoded as base64
- **WHEN** the image is processed once alone (batch size 1)
- **AND** the same image is processed with other images (batch size 2 or 3)
- **THEN** the OCR output text MUST be byte-for-byte identical in both cases

#### Scenario: Concurrent requests maintain determinism
- **GIVEN** 3 concurrent API requests with the same image
- **WHEN** all requests are processed simultaneously
- **THEN** all 3 responses MUST contain identical OCR output text

### Requirement: Batch-Invariant Operations Library Integration
The system SHALL use the `batch_invariant_ops` library to ensure PyTorch operations produce deterministic results.

#### Scenario: Model initialization with batch-invariant mode
- **GIVEN** the FastAPI application lifespan startup
- **WHEN** the vLLM model is initialized
- **THEN** the initialization MUST occur within a `set_batch_invariant_mode()` context manager
- **AND** the context MUST remain active for all inference operations

#### Scenario: Supported operations are batch-invariant
- **GIVEN** batch-invariant mode is enabled
- **WHEN** the model performs matrix operations (mm, addmm)
- **OR** the model performs activation functions (log_softmax)
- **OR** the model performs reduction operations (mean)
- **THEN** these operations MUST use batch-invariant kernel implementations
- **AND** results MUST be independent of batch size

### Requirement: Dependency Installation
The Modal container image SHALL include the `batch_invariant_ops` library installed from its GitHub repository.

#### Scenario: Library is installed from git source
- **GIVEN** the Modal container image is built
- **WHEN** the image build process runs
- **THEN** `batch_invariant_ops` MUST be installed from `git+https://github.com/thinking-machines-lab/batch_invariant_ops.git`
- **AND** the installation MUST use `pip install -e` for editable mode

#### Scenario: Library is available in container
- **GIVEN** the Modal container image is built
- **WHEN** the Python environment is inspected
- **THEN** `batch_invariant_ops` MUST be importable
- **AND** the library version MUST be compatible with PyTorch 2.8.0

#### Scenario: Local development includes batch_invariant_ops
- **GIVEN** a developer runs `uv sync` locally
- **WHEN** dependencies are installed
- **THEN** `batch_invariant_ops` MUST be installed from git source
- **AND** the library MUST be usable with local Python 3.13+

### Requirement: Determinism Documentation
The system SHALL document the determinism guarantees and any trade-offs.

#### Scenario: Code includes determinism explanation
- **GIVEN** a developer reads the vLLM initialization code
- **WHEN** they encounter the `set_batch_invariant_mode()` context manager
- **THEN** comments MUST explain the purpose of batch-invariant operations
- **AND** comments MUST reference the library's role in ensuring reproducibility

#### Scenario: Performance trade-offs are documented
- **GIVEN** batch-invariant operations may have minor overhead
- **WHEN** developers or users review documentation
- **THEN** CLAUDE.md MUST document any performance impact
- **AND** documentation MUST explain the reproducibility vs performance trade-off
