# UUID Strategy

## Objective
Support distributed and future cross-service identity management.

## Recommended Use Cases
- External-facing identifiers
- Event payload correlation
- Records that may be created from multiple services
- Identities that must remain stable across data replication boundaries

## Strategy
- Use UUIDv7 where supported for better ordering and performance characteristics.
- Use UUIDv4 only when randomness is preferred and ordering is not critical.
- Store UUIDs as fixed-length string or binary-compatible types according to database capabilities.
- Keep a separate internal surrogate key for performance-sensitive joins when needed.

## Guidance
- Use UUIDs consistently for new cross-domain entities.
- Do not overuse UUIDs for high-volume append-only tables unless the data access pattern demands it.
