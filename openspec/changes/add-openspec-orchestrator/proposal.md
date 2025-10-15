# Proposal: Add Openspec Orchestrator for Multi-LLM Coordination

## Why

The GhostWire Refractory project needs a systematic approach to coordinate multiple LLMs using the Openspec Orchestrator pattern. This enables complex task decomposition, distributed execution across multiple models, permission management, and code patching capabilities that improve the overall system's intelligence and functionality.

## What Changes

- Create `GHOSTWIRE/openspec_orchestrator/` directory with Master, Worker, and Secondary Control components
- Add orchestrator modules: `master.py`, `llm_clients.py`, `decomposition.py`, `patch_engine.py`, `permission_manager.py`
- Implement integration module that connects orchestrator with GhostWire Refractory
- Add spec files in `openspec/specs/orchestrator/` for requirements and design
- Create comprehensive spec documentation for the orchestrator system

## Impact

- Adds a new capability **orchestrator** in `openspec/specs/orchestrator/spec.md`
- Extends benchmarking system to work with orchestrated multi-LLM tasks
- Adds permission and security considerations for multi-LLM coordination
- No breaking changes to existing APIs

## Additional Notes

- The orchestrator follows the Master, Worker, and Secondary Control architectural pattern
- Integrates with existing GhostWire features like benchmarking and GHOSTWIRE scoring
- Includes proper error handling and permission validation
