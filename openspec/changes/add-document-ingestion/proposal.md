# Proposal: Add Document Ingestion Script

## Why
The GhostWire ecosystem needs a systematic document ingestion script that supports txt/md/code inputs, chunking, optional summarization, embedding generation, and storage into the local vector DB. This enables users to easily import their documents for later retrieval and RAG operations.

## What Changes
- Create `scripts/import_documents.py` with CLI flags, chunking, optional summarization, and use of existing embedding generation.
- Add a `pytest` marker `@pytest.mark.ingestion` and update imports.
- Update CI workflow to run ingestion tests separately.
- Add new spec requirement for document ingestion.

## Impact
- Adds a new capability **document-ingestion** in `openspec/specs/core/spec.md`.
- No change to runtime APIs.

## Additional Notes
- Ingestion may be time-consuming; it should be run on dedicated CI jobs.
- Documents are stored with embeddings in the local vector DB.
- Metrics are logged to the console and can be parsed by downstream tooling.