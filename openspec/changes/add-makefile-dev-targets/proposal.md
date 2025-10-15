<!-- OPENSPEC:START -->

# Proposal: Add Makefile with common dev targets

Status: proposed

Owners: @hsmalley

## Summary

Add a simple `Makefile` with targets: `setup`, `run`, `seed`, `test`, and `lint`. This offers a minimal, cross-shell dev entrypoint for laptop users who prefer explicit commands.

## Motivation

Many local developers prefer a Makefile to provide a consistent set of commands. It's lightweight and doesn't require extra tooling.

## Scope

- Add `Makefile` with targets:
  - `setup`: create venv and install editable package
  - `run`: run `scripts/run_local.sh` or module
  - `seed`: run seeder script
  - `test`: run pytest
  - `lint`: run ruff (if available)
- Document usage in README.

## Acceptance criteria

1. `Makefile` present at repo root with described targets.
2. Running `make run` starts the app locally.

## Implementation plan

1. Add `Makefile` with simple recipes and comments.
2. Update README with usage.

<!-- OPENSPEC:END -->
