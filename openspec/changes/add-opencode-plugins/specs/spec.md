# Spec: opencode plugins for GhostWire

Capability: integration

Requirement: Add a plugin system that allows opencode to hook into GhostWire’s orchestrator, providing custom LLM wrappers, tokenizers, or cache layers.

Acceptance criteria:
- A `plugins/` package exists under `python/ghostwire/`.
- Plugins expose a `register()` function that the orchestrator calls during init.
- Sample plugin for a dummy LLM client is included and documented.
- Unit tests validate plugin registration and basic functionality.
