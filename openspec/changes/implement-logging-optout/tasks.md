<!-- OPENSPEC:START -->
# Tasks: implement-logging-optout

- id: 1
  title: Add logging settings
  owner: @hsmalley
  estimate: 0.25h
  description: |
    Add LOG_LEVEL, LOG_FILE, LOG_FORMAT, and GHOSTWIRE_NO_EMOJI to `python/config/settings.py` using Pydantic BaseSettings.

- id: 2
  title: Implement logging initializer
  owner: @hsmalley
  estimate: 0.75h
  description: |
    Create or update a central logging initialization (e.g., `python/ghostwire/logging_config.py`) to set Python logging handlers and formatters based on settings, supporting plain, emoji, and JSON formats.

- id: 3
  title: Update existing logging usage
  owner: @hsmalley
  estimate: 0.5h
  description: |
    Replace direct emoji decoration around log calls with formatter-driven decorations where practical. Document any exceptions.

- id: 4
  title: Add unit tests
  owner: @hsmalley
  estimate: 0.5h
  description: |
    Add tests verifying that when `GHOSTWIRE_NO_EMOJI=1` logs are plain and that when `LOG_FORMAT=json` logs are valid JSON.

- id: 5
  title: Docs update
  owner: @hsmalley
  estimate: 0.25h
  description: |
    Update `CONTRIBUTING.md` (or README) with instructions for disabling emoji logs (examples using env vars) and the rationale.

<!-- OPENSPEC:END -->
