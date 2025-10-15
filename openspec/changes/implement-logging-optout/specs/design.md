<!-- OPENSPEC:START -->
# Design: structured logging and emoji opt-out

Decisions:

- Add `LOG_FORMAT` with values `plain|emoji|json` and `GHOSTWIRE_NO_EMOJI` as an alias to force `plain`.
- Implement logging initialization in a new `python/ghostwire/logging_config.py` module and call it from application entrypoints.
- Use a formatter class to inject or strip emoji/ANSI sequences based on config.

Testing:

- Add unit tests that capture logger output and assert format changes based on env settings.

<!-- OPENSPEC:END -->
