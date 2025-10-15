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

It will NOT:

- change the OpenSpec blocks (do not modify `<!-- OPENSPEC:START -->` sections).
- change runtime behaviour (unless a follow-up is accepted to implement a logger opt-out; see Risks & Follow-ups).

## Acceptance criteria

1. `CONTRIBUTING.md` exists at repo root and is readable.
2. It clearly explains where to use the project's theme and where to use neutral tone.
3. It documents an opt-out for emoji/ANSI logs (example env var e.g. `GHOSTWIRE_NO_EMOJI=1`) and notes how to implement it in logger code, or points to the file to edit if present.
4. It provides a simple, alternate run snippet for contributors who don't have `uv` (venv + `PYTHONPATH=python uv run python -m python.ghostwire.main`).
5. A one-line link to `CONTRIBUTING.md` is added to `README.md` (or the proposal provides the exact insertion so it can be applied separately).
6. No CI or runtime tests break; change is docs-only.

## Implementation plan

1. Create `CONTRIBUTING.md` with the sections: Purpose, Where to use the flavor, When to avoid it, Emoji/log opt-out, Simple run instructions, Links.
2. Add a 1-line link in `README.md` under Development Setup (this can be a separate, tiny PR if preferred).
3. Optionally run a markdown linter or visually inspect the docs.
4. If maintainers want, follow up with an implementation PR to add an actual logger flag/env handling to disable emoji/ANSI output (out of scope for this proposal).

## Risks & follow-ups

- Risk: The proposal suggests an env var to opt-out of emoji/ANSI that does not exist yet. Mitigation: mark the env var as a recommended example and offer a follow-up implementation to wire it into the logging configuration.
- Follow-up: Implement logger opt-out (small code change in the logging config) and add a test verifying logs are plain when the env var is set.

## Timeline

This is a small docs PR; estimated effort 15–30 minutes to author and land.

## Related

- `GHOSTWIRE_GPT/GHOSTWIRE_THEME.md`
- `GHOSTWIRE_GPT/GHOSTWIRE_FLAVOR.md`
- `AGENTS.md`

<!-- OPENSPEC:END -->
