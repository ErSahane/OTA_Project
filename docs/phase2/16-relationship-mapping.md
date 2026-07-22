# Relationship Mapping

## Mapping Strategy
Relationships are defined by the natural ownership and lifecycle dependencies of the business domain.

## Core Mappings
- User -> Customer Profile: one-to-one
- User -> Agent Profile: one-to-one
- Customer Profile -> Bookings: one-to-many
- Booking -> Booking Items: one-to-many
- Booking -> Travelers: one-to-many
- Booking -> Payments: one-to-many
- Booking -> Refunds: one-to-many
- Booking -> Support Tickets: one-to-many
- Supplier -> Supplier Products: one-to-many
- Booking Item -> Fare Rule: many-to-one
- Corporate Account -> Bookings: one-to-many

## Design Notes
- Use explicit foreign keys for all required relationships.
- Use join tables only for many-to-many relationships.
- Where historical versions are required, keep a versioned or event-based representation rather than overwriting parent references.
