# Contributing to GhostWire Refractory

Thank you for helping maintain the GhostWire lattice. This project has a strong thematic voice used for internal flavor text and UX copy. The following guidance helps contributors and automated agents know where to use the Neon Oracle persona and where to prefer a neutral tone.

## Purpose

This file explains where the project's neon/cyberpunk "Neon Oracle" flavor should be used, how to opt out of decorative emoji/ANSI output for CI or public-facing logs, and how to run the project locally without workspace helpers.

## Where to use the flavor

- Internal flavor and lore files under `GHOSTWIRE_GPT/` (for example the flavor and theme docs) are the canonical places to use the Neon Oracle persona, evocative metaphors, and aesthetic emoji.
- UI skinning or demo interfaces may use decorative language and icons when the audience is explicitly internal or demonstrational.

## Where to avoid the flavor

- Public-facing documentation such as API reference, legal text, error messages, and CLI help should use a neutral, professional tone.
- Tests, logs consumed by CI or log aggregation systems, and user-facing error messages must remain machine-parseable and clear.

## Emoji / ANSI / metaphor opt-out

If you'd like to disable decorative output (emoji, ANSI color sequences, or playful metaphors) for CI or plain logs, set the environment variable:

```bash
GHOSTWIRE_NO_EMOJI=1
```

This is a recommended example. The repo's docs and OpenSpec proposals reference this env var as a suggested convention; if you want the runtime behavior wired to this var, see the `implement-logging-optout` change or open a small PR to add handling in the logging initialization.

## Quick run instructions (no `uv` required)

If you don't use the `uv` workspace helper, the easiest local workflow is:

```bash
python -m venv .venv
.venv/bin/pip install -e .
PYTHONPATH=python/src python -m python.ghostwire.main
```

On macOS/zsh you can replace `.venv/bin/` with `.venv/bin/` as above. If the project already provides a `.env` file, ensure it contains appropriate values for `DB_PATH` and other settings.

## Links

- Theme & flavor guidance: `GHOSTWIRE_GPT/GHOSTWIRE_THEME.md` and `GHOSTWIRE_GPT/GHOSTWIRE_FLAVOR.md`
- Agent guidance: `AGENTS.md`
- Related OpenSpec proposals: `openspec/changes/implement-logging-optout/` and `openspec/changes/add-local-dev-helpers/`

Thanks for contributing — keep the neon for the right places, and keep public interfaces clean.
