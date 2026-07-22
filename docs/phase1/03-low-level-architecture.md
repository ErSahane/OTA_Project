# Low-Level Architecture

## Service Design Principles
- Each service owns a bounded business capability.
- Service contracts are versioned and documented.
- Services communicate through synchronous APIs and asynchronous events.
- Failures are isolated to prevent cascading outages.

## Recommended Service Components
### Booking Service
- Booking orchestration
- Availability validation
- Passenger and itinerary handling
- Status management

### Search Service
- Query normalization
- Supplier fan-out
- Response aggregation
- Ranking and filtering

### Pricing Service
- Fare calculation
- Rule evaluation
- Ancillary pricing
- Currency conversion

### Payment Service
- Payment initiation
- Payment confirmation
- Refund orchestration
- Settlement reconciliation

## Internal Design Guidance
- Use dependency inversion for integrations.
- Implement idempotency for all external calls and workflows.
- Separate read and write models where appropriate.
- Use event sourcing or outbox patterns for critical transactional reliability.
