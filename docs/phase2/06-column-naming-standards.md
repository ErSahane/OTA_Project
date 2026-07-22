# Column Naming Standards

## Principles
- Use lowercase snake_case.
- Use descriptive, role-based names.
- Prefer business names over technical names where possible.
- Avoid abbreviations that reduce clarity.

## Recommended Patterns
- id for primary key
- created_at, updated_at, deleted_at
- customer_id, booking_id, supplier_id
- status_code, currency_code, country_code
- is_active, is_deleted, is_primary

## Standards for Boolean Columns
- Use is_ or has_ prefixes.
- Example: is_deleted, is_refundable

## Standards for Foreign Keys
- Use the referenced entity name plus _id.
- Example: booking_id, parent_booking_id
