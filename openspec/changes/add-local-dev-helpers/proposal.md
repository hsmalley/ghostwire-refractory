<!-- OPENSPEC:START -->
# Proposal: Add local developer helpers (.env.example + run script)

Status: proposed

Owners: @hsmalley

## Summary

Add a tiny set of local-development helpers aimed at laptop-first contributors: a `.env.example` with common settings, a simple run script (`scripts/run_local.sh`) that creates a venv, installs editable package, and runs the app module, and a short README snippet showing the commands. This change reduces friction for contributors who don't have the `uv` helper and prefer a minimal, explicit local workflow.

## Motivation

Many contributors run the project locally on laptops and may not have the `uv` workspace tooling. A small, explicit set of local helpers improves onboarding and makes quick testing easier without changing runtime behavior or CI.

## Scope

This is a small docs + scripts change. It will:

- Add `.env.example` at repo root containing common env names (e.g., DB_PATH, LOG_LEVEL, LOCAL_OLLAMA_URL).
- Add `scripts/run_local.sh` (POSIX shell) that:
  - creates and activates a venv (idempotent),
  - installs the package in editable mode,
  - copies `.env.example` to `.env` if no `.env` present,
  - runs `PYTHONPATH=python/src python -m python.ghostwire.main`.
- Add a one-line snippet to `README.md` under Development Setup pointing to the script.

It will NOT change runtime configuration or CI pipelines.

## Acceptance criteria

1. `.env.example` exists and documents the common environment variables.
2. `scripts/run_local.sh` exists, is executable, and contains the described steps.
3. `README.md` contains a one-line pointer to the script under Development Setup.
4. No changes to CI or production behavior.

## Implementation plan

1. Create `.env.example` with reasonable defaults and comments.
2. Add `scripts/run_local.sh` with clear, idempotent steps.
3. Update `README.md` with one-line pointer.
4. Open a small PR and request review.

## Risks & follow-ups

- Risk: The script may behave differently on non-POSIX shells; mitigation: document usage for zsh/bash and keep the script portable.
- Follow-up: If maintainers prefer, convert to a Makefile target or add a `dev` task to `pyproject` scripts.

## Timeline

Estimated 15–30 minutes to author and land.

<!-- OPENSPEC:END -->
