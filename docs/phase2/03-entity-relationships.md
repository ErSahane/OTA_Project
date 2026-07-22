# Entity Relationships

## Relationship Summary
- One User may have one Customer Profile or one Agent Profile.
- One Customer Profile may have many Bookings.
- One Booking may have many Booking Items.
- One Booking may have many Travelers.
- One Booking may have many Payments.
- One Booking may have many Refunds.
- One Booking may have many Support Tickets.
- One Supplier may have many Supplier Products.
- One Supplier Product may be referenced by many Booking Items.
- One Booking Item may have one Fare Rule.
- One Booking may be linked to one Corporate Account where applicable.

## Relationship Notes
- Relationships should be modeled using explicit foreign keys and referential constraints.
- Status transitions should be persisted in the domain record rather than inferred from transient state.
- Cross-entity references should be immutable where historical integrity matters.
