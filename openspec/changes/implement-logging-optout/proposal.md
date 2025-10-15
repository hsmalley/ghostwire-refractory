<!-- OPENSPEC:START -->

# Proposal: Implement structured logging and emoji/ANSI opt-out

Status: proposed

Owners: @hsmalley

## Summary

Implement a configurable logging configuration that supports structured (JSON) logging, configurable log level and log file, and an environment-variable driven opt-out for emoji/ANSI/emoji decorations used in internal logs. Provide a small test and docs so contributors can disable colorful output in CI or log aggregation.

## Motivation

The project's docs and flavor files encourage ANSI/emoji-rich logs for neon style, but maintainers and CI systems need plain, parseable logs. `openspec/specs/config/spec.md` already requires configurable logging settings. Additionally, repository reviews note logging improvements as an item. Implementing structured logging with an explicit opt-out addresses multiple needs:

- makes logs machine-friendly for production and aggregation,
- allows contributors to keep neon-style logs locally while disabling them in CI,
- satisfies spec requirements for configurable logging.

## Scope

This change will:

- Add configuration settings to `python/config/settings.py` (or existing settings) for LOG_LEVEL, LOG_FILE, LOG_FORMAT (plain|emoji|json), and GHOSTWIRE_NO_EMOJI (boolean).
- Update the project's logging initialization (likely in `python/ghostwire/main.py` or a central logging module) to honor these settings and enable JSON/structured formatting when requested.
- Add a small unit test verifying that when `GHOSTWIRE_NO_EMOJI=1` or LOG_FORMAT=json the logger outputs plain or JSON logs (respectively).
- Update docs (`CONTRIBUTING.md` or `README.md`) to mention how to disable emoji logs.

Out of scope: migrating existing log consumers or adding external log shipping integrations.

## Acceptance criteria

1. New config settings exist and read from environment or .env: LOG_LEVEL, LOG_FILE (optional), LOG_FORMAT (one of plain|emoji|json), and GHOSTWIRE_NO_EMOJI (alias to force plain).
2. Logging initialization respects these settings and produces the expected format.
3. Unit test(s) validate plain and JSON output modes.
4. `CONTRIBUTING.md` or README updated with instructions to disable emoji/ANSI logs.
5. No behavioral changes to core services other than logging; CI remains green.

## Implementation plan

1. Add new settings to `python/config/settings.py` (Pydantic BaseSettings).
2. Create/modify `python/ghostwire/logging_config.py` (or similar) to initialize Python logging accordingly.
3. Replace existing ad-hoc emoji decorations (if present) with formatter-level behavior.
4. Add tests under `python/tests/unit/test_logging.py`.
5. Update docs to reference the new settings and examples.

## Risks & mitigation

- Risk: Other code constructs may append emojis directly before logging calls. Mitigation: search for emoji usage in logs and convert to formatters where feasible; otherwise note exceptions in the implementation.
- Risk: Formatting change may break human workflows; mitigation: default LOG_FORMAT should mirror current behavior (emoji) or a conservative default (plain) and be documented.

## Timeline

Small maintenance change; estimated 1–2 hours including tests and docs.

<!-- OPENSPEC:END -->
