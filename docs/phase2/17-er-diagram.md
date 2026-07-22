# ER Diagram

## Conceptual ER Diagram
```text
User 1---1 CustomerProfile
User 1---1 AgentProfile
CustomerProfile 1---* Booking
Booking 1---* BookingItem
Booking 1---* Traveler
Booking 1---* Payment
Booking 1---* Refund
Booking 1---* SupportTicket
Supplier 1---* SupplierProduct
SupplierProduct 1---* BookingItem
BookingItem *---1 FareRule
CorporateAccount 1---* Booking
```

## Diagram Notes
- The booking entity is the central aggregate for the MVP domain.
- Suppliers and fare rules are modeled independently to support future inventory expansion.
- Support and audit entities remain linked to the booking lifecycle for traceability.
