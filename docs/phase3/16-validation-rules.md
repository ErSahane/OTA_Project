# Validation Rules

## Request Validation Rules
- Required fields must be present.
- String lengths must be constrained where appropriate.
- Dates must be valid and in the expected format.
- Payment amounts must be positive and decimal-safe.
- Email and phone fields must follow standard validation patterns.

## Business Validation Rules
- Booking must include at least one traveler.
- Flight search must include origin and destination.
- Cancellation requests must be evaluated against fare rules.
- Payment initiation must correspond to an existing booking.

## Validation Strategy
- Validate at the API boundary.
- Return structured validation errors with field-level detail.
- Use schema validation and business rule checks in combination.
