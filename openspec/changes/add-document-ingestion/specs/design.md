<!-- OPENSPEC:START -->
# Design: document ingestion script

⚡️🌈 Neon Oracle Note: This design spec wears neon and chrome — concise, vivid, and a little electric. Use tasteful emoji where helpful for clarity, but keep technical details authoritative and machine-friendly. 🤖✨

Decisions:

- Provide a simple CLI that accepts a file or directory and an optional `--dry-run` flag.
- Reuse existing embedding service code where possible; fall back to an environment-configured local embedder.
- Chunking: default to 500 token/word chunks with overlap; configurable via CLI flags.
- Summarization: optional via `--summarize` flag; use existing summarization service.

Security & Safety:

- Do not overwrite DB schema; insert only.
- Provide a `--confirm` flag for destructive actions (not used by default).
- Validate all input files and directories before processing.
- Use secure temporary file handling where needed.

Performance & Efficiency:

- Process files in parallel where possible.
- Use connection pooling for database operations.
- Cache embedding service connections.
- Implement proper error handling and retry logic.

<!-- OPENSPEC:END -->