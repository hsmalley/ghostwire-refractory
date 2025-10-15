<!-- OPENSPEC:START -->
# Design: local dev helpers

Decisions:

- Keep `scripts/run_local.sh` POSIX-compatible and idempotent.
- Prefer vanilla `venv` over external tooling so it works on macOS and Linux.
- Do not modify runtime config; only provide helpful defaults in `.env.example`.

Security:

- No secrets committed. `.env.example` contains placeholders only.

<!-- OPENSPEC:END -->
