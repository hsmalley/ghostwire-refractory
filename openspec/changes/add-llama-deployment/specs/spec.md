# Spec: llamafile deployment via ssh

Capability: deployment

Requirement: Deploy llamafiles as systemd units on remote hosts via SSH, allowing GhostWire to control them over their local APIs.

Acceptance criteria:

- A deployment script resides under `scripts/llama_deploy.py`.
- The script uses `fabric` (or similar) to SSH into a host, place the llamafile, generate a systemd unit file, and enable/start the service.
- Remote connectivity is verified with a simple health endpoint.
- Unit tests cover packaging of unit file and SSH command construction.
