# Design: opencode plugins

Decisions:
- Create `python/ghostwire/plugins/` package.
- Each plugin defines a `register(orchestrator: Orchestrator)` function.
- The orchestrator imports `ghostwire.plugins` and executes `register()` on discovered modules.
- Provide a `dummy_llm.py` plugin example.
