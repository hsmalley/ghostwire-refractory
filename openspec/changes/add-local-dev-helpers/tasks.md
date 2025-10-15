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

<!-- OPENSPEC:END -->
