## ADDED Requirements
### Requirement: Local Development Helpers
The project SHALL provide a minimal set of scripts and a `.env.example` for contributors to bootstrap a local environment.

#### Scenario: .env.example Exists
- **WHEN** cloning the repo
- **THEN** a `.env.example` file exists and lists typical environment variables.

#### Scenario: run_local.sh Exists
- **WHEN** running `sh scripts/run_local.sh`
- **THEN** a virtual environment is created/activated, the package is installed editable, and the app runs.

#### Scenario: README Snippet
- **WHEN** opening `README.md`
- **THEN** a one‑liner pointing to `scripts/run_local.sh` is present.
