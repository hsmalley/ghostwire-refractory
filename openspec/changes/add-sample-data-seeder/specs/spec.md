<!-- OPENSPEC:START -->
# Spec: sample data seeder

Capability: developer-experience

Requirement: Provide `scripts/seed_sample_data.py` that populates a local SQLite DB with safe, idempotent sample data for local testing.

Acceptance criteria:

- Script exists and is runnable: `python scripts/seed_sample_data.py`
- Script respects configured `DB_PATH` and is non-destructive by default
- README documents usage

<!-- OPENSPEC:END -->
