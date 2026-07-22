# Versioning Strategy

## Versioning Approach
- Version all public APIs through the URI path.
- Use major versions such as /v1, /v2.
- Introduce additive changes in a backward-compatible manner.
- Deprecate old versions with documented timelines.

## Versioning Rules
- Breaking changes must require a new major version.
- Minor changes should preserve contract compatibility.
- API contracts should be reviewed before release.

## Recommended Pattern
- /api/v1/users
- /api/v1/bookings
- /api/v1/flight-search
