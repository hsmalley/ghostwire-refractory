## ADDED Requirements

### Requirement: Sample Data Seeder

The project SHALL provide a script that seeds local SQLite with sample sessions, messages, and embeddings.

#### Scenario: Seeder Script Exists

- **WHEN** cloning the repo
- **THEN** `scripts/seed_sample_data.py` exists and can be executed.

#### Scenario: Idempotent

- **WHEN** running `python scripts/seed_sample_data.py` multiple times
- **THEN** no duplicate rows are inserted without explicit flag.

#### Scenario: Documentation

- **WHEN** opening `README.md`
- **THEN** a note explaining how to run the seeder is present.
