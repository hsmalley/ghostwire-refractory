## ADDED Requirements

### Requirement: Makefile Development Targets

The project SHALL offer a `Makefile` providing common development tasks.

#### Scenario: Makefile Exists

- **WHEN** opening the repo
- **THEN** a `Makefile` with targets `setup`, `run`, `seed`, `test`, and `lint` is present.

#### Scenario: README Example

- **WHEN** viewing `README.md`
- **THEN** a short example of using `make run` is included.
