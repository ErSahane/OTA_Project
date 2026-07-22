# Admin APIs

## Endpoints
### Admin Dashboard Summary
- GET /api/v1/admin/dashboard

### Manage Users
- GET /api/v1/admin/users
- GET /api/v1/admin/users/{userId}

### Manage Bookings
- GET /api/v1/admin/bookings
- GET /api/v1/admin/bookings/{bookingId}

### Manage Tickets
- GET /api/v1/admin/tickets
- PUT /api/v1/admin/tickets/{ticketId}

## Notes
- Admin APIs should be restricted to privileged roles.
- Audit and action logs should be available for admin review.
