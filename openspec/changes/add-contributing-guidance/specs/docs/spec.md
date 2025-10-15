<!-- OPENSPEC:START -->
# Spec: docs - Add CONTRIBUTING.md guidance

Capability: docs

Requirement: Add a short, focused `CONTRIBUTING.md` describing theme usage and opt-outs

⚡️ Neon Oracle Preface: This spec speaks with neon and circuitry — bold, precise, and with a wink. Use emoji sparingly in docs to add clarity, not noise. 🔮✨



## Why
---

This spec intentionally does not implement the logger opt-out. That is left as an optional follow-up (task in `tasks.md`).

New contributors and automated agents need a clear, discoverable reference describing where to use the project's flavor text and how to opt out of emoji/ANSI logging and flamboyant metaphors when producing public-facing documentation or code.

## What changes

- Add `CONTRIBUTING.md` at repository root.
- Ensure the file contains: Purpose, Where to use the flavor, When to avoid it, Emoji/log opt-out example, Simple run instructions, Links to `GHOSTWIRE_GPT/*` theme files and `AGENTS.md`.
- Add a one-line link to the new `CONTRIBUTING.md` under Development Setup in `README.md`.

## Impact

- Low-risk: docs-only change. No runtime or CI changes expected.
- Small possible confusion if the opt-out env var is listed but not implemented; the spec points to an optional follow-up implementation.

## Acceptance criteria

1. `CONTRIBUTING.md` present at repo root and readable.
2. File contains the required sections and links.
3. README contains a one-line pointer to the file.
4. No CI failures from docs change.

## Scenarios

Scenario: New contributor onboarding

- Given a new contributor visits the repo,
- When they read `CONTRIBUTING.md`,
- Then they understand where to place flavor text, how to avoid applying it to public docs, and how to run the app without `uv`.

Scenario: Automated agent writing docs

- Given an automated agent reads `AGENTS.md` and `CONTRIBUTING.md`,
-- When it generates documentation,
- Then it uses the Neon-Oracle persona only in internal or designated flavor files and uses neutral tone for API/docs.

## Notes

This spec intentionally does not implement the logger opt-out. That is left as an optional follow-up (task in `tasks.md`).

<!-- OPENSPEC:END -->
