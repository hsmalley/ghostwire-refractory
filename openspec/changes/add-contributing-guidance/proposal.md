<!-- OPENSPEC:START -->
# Proposal: Add CONTRIBUTING.md with theme guidance and opt-outs

Status: proposed

Owners: @hsmalley

## Summary

Add a short, focused `CONTRIBUTING.md` at the repository root that documents the project's thematic flavor (neon/cyberpunk, Neon Oracle voice), clarifies where to use flamboyant flavor text vs. neutral, public-facing documentation, and provides simple opt-outs (emoji/ANSI logging, metaphors) plus a straightforward "how to run" section for contributors who don't use the repo's `uv` helper.

## Motivation

This repository contains strong, intentional theme files (`GHOSTWIRE_GPT/GHOSTWIRE_THEME.md`, `GHOSTWIRE_GPT/GHOSTWIRE_FLAVOR.md`) and tooling guidance in `AGENTS.md` instructing AI contributors to adopt a Neon Oracle persona. New contributors (and automated agents) may be surprised by the style and unsure where it's appropriate. A short `CONTRIBUTING.md` reduces onboarding friction by:

- clarifying the intended audience for the flamboyant language (internal docs, flavor text, UI skinning) vs. neutral/public docs (API docs, error messages, legal text),
- providing minimal alternative run instructions for contributors who don't have `uv` installed,
- linking to the canonical theme/flavor docs and to `AGENTS.md` so contributors and automated agents can follow the project's conventions.

## Scope

This is a docs-only change. It will:

- Add `CONTRIBUTING.md` at repository root.
- Add a single-line link in `README.md` under Development Setup (optional; proposal includes suggested text).

## Acceptance criteria

1. `CONTRIBUTING.md` present and contains: Purpose, Where to use the flavor, When to avoid it, Emoji/log opt-out example, Simple run instructions, Links to `GHOSTWIRE_GPT/*` theme files and `AGENTS.md`.
2. `README.md` contains a one-line pointer under Development Setup linking to `CONTRIBUTING.md`.

<!-- OPENSPEC:END -->