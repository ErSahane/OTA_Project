# Filtering and Sorting

## Filtering
Use query parameters for field-based filtering.

### Example
- GET /api/v1/bookings?status=PENDING&customerId=123
- GET /api/v1/users?role=AGENT

## Sorting
Use a sort parameter with a field and direction.

### Example
- GET /api/v1/bookings?sort=createdAt:desc
- GET /api/v1/users?sort=fullName:asc

## Rules
- Filter parameters should be explicit and documented.
- Sorting should be deterministic and index-friendly where possible.
- Unsupported filter combinations should return validation errors.
