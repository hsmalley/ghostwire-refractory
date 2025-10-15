## ADDED Requirements
### Requirement: Expose Prometheus metrics endpoint
The system SHALL expose a `/metrics` endpoint that streams Prometheus‑compatible metrics, including:
- Latency histograms per API route.
- A cumulative counter of total API calls.


#### Scenario: /metrics responds with Prometheus format
- **WHEN** a client sends a GET request to `/metrics`
- **THEN** the server returns a 200 response with `Content-Type: application/vnd.google.protobuf` (or plain text) containing the metrics.

#### Scenario: Latency metrics are recorded
- **WHEN** an API route is invoked
- **THEN** the corresponding histogram bucket is incremented with the observed latency.

