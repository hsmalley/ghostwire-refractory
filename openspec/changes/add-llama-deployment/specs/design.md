# Design: llamafile deployment

Decisions:
- Use `fabric` to manage SSH. Optional `mitogen` for performance.
- `scripts/llama_deploy.py` will accept a host list, llama file path, and service name.
- Generates a systemd unit with ExecStart pointing to the llamafile.
- Remote checks via a health‑check endpoint exposed by the llamafile.
- Provide unit tests using `unittest.mock` to stub SSH connections.
