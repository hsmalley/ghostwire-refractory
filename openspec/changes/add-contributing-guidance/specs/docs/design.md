<!-- OPENSPEC:START -->
# Design: CONTRIBUTING.md placement and content

Location: `CONTRIBUTING.md` at repository root

Design goals:

- Keep the file short (one screen if possible) and pragmatic.
- Make the distinction between internal flavor docs and public-facing docs explicit.
- Provide an opt-out recommendation for emoji/ANSI logs as an example (env var) and reference where to implement it.
- Provide a minimal run snippet for contributors without `uv`.

Content sketch:

- Purpose: one paragraph
- Where to use the flavor: list of directories and examples
- When to avoid the flavor: examples (API docs, error messages, legal text)
- Opt-outs: example env var `GHOSTWIRE_NO_EMOJI=1` and a note pointing to logging config
- Run instructions: venv -> pip install -e . -> run module
- Links: theme docs and AGENTS.md

<!-- OPENSPEC:END -->
