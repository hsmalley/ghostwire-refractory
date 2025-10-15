## ADDED Requirements
### Requirement: Document Ingestion Script
The project SHALL provide a CLI script `scripts/import_documents.py` supporting txt/md/code inputs, chunking, optional summarization, embedding generation, and storage into the local vector DB.

#### Scenario: Script Exists
- **WHEN** cloning the repo
- **THEN** `scripts/import_documents.py` exists and can be executed.

#### Scenario: CLI Flags
- **WHEN** running `python scripts/import_documents.py --help`
- **THEN** the script shows available CLI flags including `--dry-run` and optional summarization flag.

### Requirement: Document Ingestion Tests
The project SHALL provide unit and integration tests for the document ingestion script.

#### Scenario: Unit Tests Exist
- **WHEN** running `pytest -m ingestion`
- **THEN** all document ingestion unit tests are executed.

#### Scenario: Integration Tests Exist
- **WHEN** running `pytest -m integration`
- **THEN** document ingestion integration tests are included.

### Requirement: Document Ingestion Documentation
The project SHALL document the document ingestion script usage.

#### Scenario: README Documentation
- **WHEN** opening `README.md` or `scripts/README.md`
- **THEN** instructions on running the document ingestion script are present.

#### Scenario: CLI Help
- **WHEN** running `python scripts/import_documents.py --help`
- **THEN** helpful usage information is displayed.