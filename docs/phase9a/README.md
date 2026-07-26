# Phase 9A - Booking Foundation

The booking foundation introduces a provider-neutral booking domain behind `/api/v1/bookings/`.

Main capabilities:

- held booking session management
- booking token and booking reference generation
- passenger and contact validation
- SSR capture per passenger
- fare revalidation and seat-availability validation
- booking lifecycle state machine
- provider reservation creation behind the integration abstraction
- temporary hold handling
- idempotency protection
- distributed locking through Django cache
- transactional persistence and audit logging

Key endpoints:

- `POST /api/v1/bookings/sessions/`
- `POST /api/v1/bookings/confirm/`
- `GET /api/v1/bookings/`
- `GET /api/v1/bookings/{reference}/`
- `GET /api/v1/bookings/{reference}/status/`
