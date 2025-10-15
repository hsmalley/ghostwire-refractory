<!-- OPENSPEC:START -->
# Tasks: add-local-dev-helpers

- id: 1
  title: Add .env.example
  owner: @hsmalley
  estimate: 0.1h
  description: |
    Create `.env.example` with common variables: DB_PATH, LOG_LEVEL, LOCAL_OLLAMA_URL, EMBED_DIM, and a comment about disabling emoji logs.

- id: 2
  title: Add run_local.sh script
  owner: @hsmalley
  estimate: 0.2h
  description: |
    Create `scripts/run_local.sh` which sets up a venv, installs the package in editable mode, copies `.env.example` to `.env` if missing, and runs the module.

- id: 3
  title: Update README
  owner: @hsmalley
  estimate: 0.05h
  description: |
    Add a one-line pointer under Development Setup to `scripts/run_local.sh` and mention the `.env.example`.

- id: 4
  title: Review & land
  owner: Maintainers
  estimate: 0.1h
  description: |
    Open a small PR, request review, and land once approved.

## Implementation
- [x] Add `.env.example` at repo root containing common env names (DB_PATH, LOG_LEVEL, LOCAL_OLLAMA_URL, EMBED_DIM, and a comment about disabling emoji logs).
- [x] Add `scripts/run_local.sh` (POSIX shell) that:
  - creates and activates a venv (idempotent),
  - installs the package in editable mode,
  - copies `.env.example` to `.env` if no `.env` present,
  - runs `PYTHONPATH=python uv run python -m python.ghostwire.main`.
- [x] Add a one-line pointer under Development Setup in `README.md` linking to `scripts/run_local.sh` and mentioning the `.env.example`.
- [x] Review & land PR after approval.
<!-- OPENSPEC:END -->
