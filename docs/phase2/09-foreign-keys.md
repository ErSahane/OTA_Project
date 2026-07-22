# Foreign Keys

## Purpose
Enforce referential integrity between related business entities.

## Standards
- Every relationship that represents a required ownership or dependency should use a foreign key.
- Foreign keys should be indexed where the relationship is queried frequently.
- Cascade rules should be carefully limited to avoid unintended data loss.

## Recommended Patterns
- bookings.customer_id -> customers.id
- booking_items.booking_id -> bookings.id
- payments.booking_id -> bookings.id
- refunds.payment_id -> payments.id
- support_tickets.booking_id -> bookings.id

## Governance
- Avoid circular dependencies in schema design.
- Use soft-delete-aware referencing patterns where required by business rules.
