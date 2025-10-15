<!-- OPENSPEC:START -->
# Spec: structured logging and emoji opt-out

Capability: config & logging

Requirement: Add config options for `LOG_LEVEL`, `LOG_FILE`, `LOG_FORMAT`, and `GHOSTWIRE_NO_EMOJI` and provide a central logging initialization that respects these settings.

Acceptance criteria:

- Settings added to `python/config/settings.py` (Pydantic BaseSettings)
- Logging initialization module created/updated to honor `LOG_FORMAT`/`GHOSTWIRE_NO_EMOJI`
- Unit test(s) validate plain and JSON log outputs

<!-- OPENSPEC:END -->
