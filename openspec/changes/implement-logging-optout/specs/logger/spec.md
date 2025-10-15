## ADDED Requirements

### Requirement: Logging Opt‑Out

The project SHALL expose an environment variable `GHOSTWIRE_NO_EMOJI` that, when set, forces the logger to output plain text without emoji or ANSI codes.

#### Scenario: Flag Set

- **WHEN** `GHOSTWIRE_NO_EMOJI=1` is present
- **THEN** all log messages contain no ANSI or emoji sequences.

#### Scenario: Default Behaviour

- **WHEN** the flag is absent
- **THEN** logs keep their current emoji/ANSI style.
