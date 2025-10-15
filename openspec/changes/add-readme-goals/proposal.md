<!-- OPENSPEC:START -->

# Proposal: Add "Project goals" summary to README

Status: proposed

Owners: @hsmalley

## Summary

Add a short "Project goals" section to `README.md` that summarizes `GHOSTWIRE_GPT/GHOSTWIRE_GOALS.md` in one clear paragraph so newcomers immediately understand the laptop-first sqlite-as-cache architecture and the intended flow (user -> sqlite -> remote LLM).

## Motivation

The goals file contains useful context, but newcomers often read `README.md` first. A concise goals paragraph reduces initial confusion and sets expectations for local-first usage.

## Scope

- Add a short "Project goals" subsection under Development Setup in `README.md` (2-3 sentences and a link to `GHOSTWIRE_GPT/GHOSTWIRE_GOALS.md`).
- No code changes.

## Acceptance criteria

1. `README.md` contains a visible "Project goals" subsection summarizing laptop-first intent.
2. It links to `GHOSTWIRE_GPT/GHOSTWIRE_GOALS.md` for full details.

## Implementation plan

1. Draft the 2-3 sentence summary and add to README.
2. Run a quick visual check.

## Timeline

Estimated 5–10 minutes.

<!-- OPENSPEC:END -->
