# Payment APIs

## Endpoints
### Initiate Payment
- POST /api/v1/bookings/{bookingId}/payments

### Payment Status
- GET /api/v1/payments/{paymentId}

### Refund Initiation
- POST /api/v1/payments/{paymentId}/refunds

## Notes
- Payment APIs must follow secure transaction standards.
- Payment operations should be traceable and reconcileable.
- Refund workflows should be separate from initial payment creation.
