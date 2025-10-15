## Context

The GhostWire Refractory codebase contained technical debt in the form of unused files and incomplete implementations. Following Universal Janitor principles, we needed to clean up the codebase to reduce complexity and improve maintainability.

## Goals / Non-Goals

- Goals:
  - Remove dead code and unused files
  - Implement missing functionality (HNSW backfill)
  - Extract duplicated code to shared utilities
  - Create comprehensive documentation with OpenSpec

- Non-Goals:
  - Change core functionality of the system
  - Modify the overall architecture
  - Add new features beyond cleanup

## Decisions

- Decision: Extract vector normalization to shared utility
  - Why: The same normalization logic was duplicated in the MemoryService
  - Alternative considered: Keep duplicate code - rejected for maintainability

- Decision: Implement HNSW backfill functionality instead of leaving placeholder
  - Why: The system should properly initialize with existing data
  - Alternative considered: Remove backfill completely - rejected as it would cause data loss

- Decision: Create OpenSpec documentation for all major capabilities
  - Why: To provide clear reference for the current state of the system
  - Alternative considered: Document only the changes - rejected as system needs comprehensive docs

## Risks / Trade-offs

- Risk: Removing files might break unknown dependencies
  - Mitigation: Verified files were truly unused before removal

- Risk: Changing service methods might affect calling code
  - Mitigation: Used proper imports and maintained interface compatibility

## Migration Plan

- Steps:
  1. Remove unused files
  2. Implement missing functionality
  3. Refactor duplicated code
  4. Create documentation

- Rollback: All changes are tracked in version control and can be reverted if needed

## Open Questions

- None at this time.
