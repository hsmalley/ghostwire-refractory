# Design: orchestrator API control

Decisions:
- Create a lightweight wrapper `LLMController` that holds an opencode client instance.
- The client will be initialized via `opencode.Client(api_key=os.getenv("OPENCODE_API_KEY"))`.
- Health check method calls `client.health()` and returns status.
- Provide simple test hooks for mocking the client.
