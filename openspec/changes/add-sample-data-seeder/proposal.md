<!-- OPENSPEC:START -->

# Proposal: Add sample data seeder for local development

Status: proposed

Owners: @hsmalley

## Summary

Add a small sample-data seeder script (`scripts/seed_sample_data.py`) that populates the local SQLite database with a few example sessions, messages, and synthetic embeddings. This helps laptop-first contributors quickly explore the UI and behavior without having to produce data manually.

## Motivation

Many dev flows rely on existing data. A tiny seeder script accelerates local testing and manual exploration. It should be safe (idempotent by default) and optional.

## Scope

- Add `scripts/seed_sample_data.py` that connects to the configured DB (respecting `DB_PATH` or default), creates tables if missing or uses existing schema, and inserts 5 sample sessions each with several memories. Embeddings may be small random vectors matching `EMBED_DIM`.
- Document usage in README or `scripts/README.md`.

Out of scope: production data, complex fixtures.

## Acceptance criteria

1. Script exists and is runnable: `python scripts/seed_sample_data.py`.
2. It uses configured DB_PATH or default and is idempotent (can be re-run without duplicating entries beyond a clear marker).
3. README documents how to run it.

## Implementation plan

1. Write `scripts/seed_sample_data.py` using lightweight sqlite3 and numpy (or Python's random if numpy not desired).
2. Add README snippet.
3. Land change.

## Risks & mitigation

- Risk: seeder corrupts DB schema. Mitigation: only insert into existing tables and create minimal table structures if absent, avoid destructive operations.

<!-- OPENSPEC:END -->
