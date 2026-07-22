# Cancellation APIs

## Endpoints
### Create Cancellation
- POST /api/v1/bookings/{bookingId}/cancellations

### Get Cancellation
- GET /api/v1/cancellations/{cancellationId}

### List Cancellations
- GET /api/v1/cancellations

## Notes
- Cancellation eligibility should be validated based on fare rules and supplier policy.
- Refund outcomes should be linked to the cancellation workflow.
