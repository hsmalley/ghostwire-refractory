<!-- OPENSPEC:START -->
# Spec: document ingestion script

Capability: ingestion

Requirement: Provide `scripts/import_documents.py` supporting txt/md/code inputs, chunking, optional summarization, embedding generation, and storage into the local vector DB.

Acceptance criteria:

- Script exists and supports a CLI `--dry-run` flag
- Script documents usage in README or `scripts/README.md`
- Script respects `EMBED_DIM` and other configured settings

<!-- OPENSPEC:END -->