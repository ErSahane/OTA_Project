# Table Naming Standards

## Naming Principles
- Use lowercase snake_case for table names.
- Use singular or plural consistently; plural is recommended for collection-style entities.
- Use domain-based names that reflect business meaning.
- Avoid generic names such as data or info.

## Recommended Examples
- customers
- bookings
- booking_items
- travelers
- payments
- refunds
- support_tickets
- suppliers
- fare_rules
- audit_events

## Prefix Guidelines
- Core business tables use domain names directly.
- Junction tables use both entity names joined by underscore.
- Audit tables use the audit_ prefix.
