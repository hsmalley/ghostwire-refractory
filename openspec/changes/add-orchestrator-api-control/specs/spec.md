# Spec: orchestrator API control

Capability: orchestrator

Requirement: Enable control of LLM endpoints via a compatible API such as opencode. The orchestrator should expose methods to start, stop, and query LLMs through a standardized interface.

Acceptance criteria:

- A class `LLMController` is added to `python/ghostwire/orchestrator/llm_controller.py`.
- The class can initialize an opencode API client and perform a simple health check.
- Unit tests cover initialization and health_check method.
