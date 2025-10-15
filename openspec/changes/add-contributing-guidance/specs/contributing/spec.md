## ADDED Requirements
### Requirement: Contributing Guidance
The project SHALL provide a `CONTRIBUTING.md` file that explains onboarding and theme usage.

#### Scenario: File Creation
- **WHEN** a contributor clones the repo
- **THEN** a `CONTRIBUTING.md` exists at the repository root.

### Requirement: README Link
The project SHALL put a reference to `CONTRIBUTING.md` in `README.md`.

#### Scenario: Link Exists
- **WHEN** opening `README.md`
- **THEN** a line `See [CONTRIBUTING.md](/CONTRIBUTING.md) for guidelines` is present.