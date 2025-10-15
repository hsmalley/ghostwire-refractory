## ADDED Requirements
### Requirement: Prometheus Endpoint
The project SHALL expose a `/metrics` endpoint returning Prometheus compatible metrics.

#### Scenario: Endpoint Registered
- **WHEN** the application starts
- **THEN** a route `/metrics` exists and returns a 200 status.

#### Scenario: Metrics Recorded
- **WHEN** a request hits an API route
- **THEN** a latency histogram gauge is updated for that endpoint.

## MODIFIED Requirements
*(none)*
