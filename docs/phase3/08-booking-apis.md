# Booking APIs

## Endpoints
### Create Booking
- POST /api/v1/bookings

### Get Booking
- GET /api/v1/bookings/{bookingId}

### List Bookings
- GET /api/v1/bookings

### Update Booking
- PUT /api/v1/bookings/{bookingId}

### Booking Status
- GET /api/v1/bookings/{bookingId}/status

## Notes
- Booking creation should be idempotent to support retries.
- Booking workflow should maintain consistent statuses and audit events.
