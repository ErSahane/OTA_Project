# Primary Key Strategy

## Objective
Ensure stable, scalable, and resilient identity management across distributed services.

## Recommended Strategy
- Use a surrogate numeric identity for internal high-volume tables.
- Use a UUID or ULID for globally distributed and cross-system references where necessary.
- Avoid exposing internal numeric IDs externally without a stable alias strategy.

## Guidelines
- Every table should have a single primary key.
- Composite keys should be avoided except for explicit join tables.
- Primary keys should remain immutable.

## Recommended Usage
- Use bigint for high-volume transactional tables.
- Use UUID for integration-facing or globally referenced records.
