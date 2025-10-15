<!-- OPENSPEC:START -->
# Spec: document ingestion script

⚡️🌈 Neon Oracle Note: This spec hums like neon—clear, bright, and helpful. Sprinkle emoji for readability, but keep the requirements precise and testable. 🪩📚

Capability: ingestion

Requirement: Provide `scripts/import_documents.py` supporting txt/md/code inputs, chunking, optional summarization, embedding generation, and storage into the local vector DB.

Acceptance criteria:

- Script exists and supports a CLI `--dry-run` flag
- Script documents usage in README or `scripts/README.md`
- Script respects `EMBED_DIM` and other configured settings

<!-- OPENSPEC:END -->
