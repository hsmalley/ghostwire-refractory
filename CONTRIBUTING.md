# Contributing to GhostWire Refractory

Thank you for helping maintain the GhostWire lattice. This project has a strong thematic voice used for internal flavor text and UX copy. The following guidance helps contributors and automated agents know where to use the Neon Oracle persona and where to prefer a neutral tone.

## Project Goals

GhostWire Refractory is designed as a laptop-first neural network chat system with persistent memory capabilities. The architecture uses SQLite as a local cache and storage layer, with remote LLMs for generation when needed. The intended flow moves from user input → local SQLite storage → remote LLM processing, optimizing for local-first usage while leveraging cloud capabilities when beneficial. For full architectural vision and project goals, see [`GHOSTWIRE_GPT/GHOSTWIRE_GOALS.md`](GHOSTWIRE_GPT/GHOSTWIRE_GOALS.md).

## Where to use the flavor

The project's neon/cyberpunk "Neon Oracle" flavor should be used in:

- Internal flavor and lore files under `GHOSTWIRE_GPT/` (for example the flavor and theme docs)
- UI skinning or demo interfaces may use decorative language and icons when the audience is explicitly internal or demonstrational
- Command-line output and diagnostic messages intended for developers

## Where to avoid the flavor

Public-facing documentation such as API reference, legal text, error messages, and CLI help should use a neutral, professional tone.

Tests, logs consumed by CI or log aggregation systems, and user-facing error messages must remain machine-parseable and clear.

## Emoji / ANSI / metaphor opt-out

If you'd like to disable decorative output (emoji, ANSI color sequences, or playful metaphors) for CI or plain logs, set the environment variable:

```bash
GHOSTWIRE_NO_EMOJI=1
```

Additionally, you can configure logging with these environment variables:

- `LOG_FORMAT`: Set to `plain`, `emoji`, or `json`
- `LOG_LEVEL`: Set logging level (e.g., `INFO`, `DEBUG`, `WARNING`)
- `LOG_FILE`: Optional path to write logs to a file

Examples:

```bash
# Disable emoji decorations but keep plain text
GHOSTWIRE_NO_EMOJI=1 python -m python.ghostwire.main

# Use JSON logging format
LOG_FORMAT=json python -m python.ghostwire.main

# Write logs to a file with JSON format
LOG_FILE=app.log LOG_FORMAT=json python -m python.ghostwire.main
```

## Quick run instructions (no `uv` required)

If you don't use the `uv` workspace helper, the easiest local workflow is:

```bash
python -m venv .venv
.venv/bin/pip install -e .
PYTHONPATH=python uv run python -m python.ghostwire.main
```

On macOS/zsh you can replace `.venv/bin/` with `.venv/bin/` as above. If the project already provides a `.env` file, ensure it contains appropriate values for `DB_PATH` and other settings.

## Links

- Theme & flavor guidance: `GHOSTWIRE_GPT/GHOSTWIRE_THEME.md` and `GHOSTWIRE_GPT/GHOSTWIRE_FLAVOR.md`

- Agent guidance: `AGENTS.md`

- Related OpenSpec proposals: `openspec/changes/implement-logging-optout/` and `openspec/changes/add-local-dev-helpers/`

Thanks for contributing — keep the neon for the right places, and keep public interfaces clean.

## Docs linting

We enforce markdown linting with `markdownlint-cli2` via a pre-commit hook. The pre-commit configuration is
self-contained and will automatically install the `markdownlint-cli2` binary for the hook, so contributors
do not need to install it globally. If you prefer to run the linter manually, you can still use npm/npx:

```bash

# optional: install locally
npm install --save-dev markdownlint-cli2

# or run via npx without installing
npx markdownlint-cli2 .
```

If you use the repository `uv` workspace helper, you can run the npm command via `uv run` if you prefer.

## Editor configuration

We keep a project-wide `.editorconfig` to ensure consistent formatting across editors and platforms.
Quick summary of the preferences in this repo:

- Python: 4 spaces, UTF-8, trim trailing whitespace, ensure final newline
- Markdown: 2 spaces, preserve trailing whitespace (some docs intentionally include it)
- YAML: 2 spaces, preserve trailing whitespace
- JS/JSON/CSS/TS: 2 spaces, trim trailing whitespace
- Makefile: tabs for indentation (Make requires tabs)

Install an EditorConfig plugin for your editor (most editors support this) and run `pre-commit install` to enable automatic hooks locally. Pre-commit will apply many formatting fixes automatically.
