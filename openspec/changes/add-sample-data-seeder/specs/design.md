<!-- OPENSPEC:START -->
# Design: sample data seeder

Decisions:

- Use Python's built-in `sqlite3` to avoid new runtime dependencies.
- Generate synthetic embeddings with randomized floats matching `EMBED_DIM` if no embedding service is available.
- Seeder will be idempotent by checking for an inserted marker entry.

<!-- OPENSPEC:END -->
