# REST Naming Conventions

## Resource Naming
- Use plural nouns for collections.
- Use lowercase kebab-case for path segments.
- Keep paths resource-oriented and hierarchical.

## Examples
- GET /api/v1/users
- GET /api/v1/users/{userId}
- POST /api/v1/bookings
- GET /api/v1/bookings/{bookingId}
- POST /api/v1/bookings/{bookingId}/payments
- POST /api/v1/bookings/{bookingId}/cancellations

## Action Naming
- Prefer resource actions over verb-based endpoints.
- Use sub-resources for related entities.
- Use query parameters for filtering and pagination.
