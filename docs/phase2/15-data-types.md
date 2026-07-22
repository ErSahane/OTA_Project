# Data Types

## General Principles
Use the most precise built-in data type available for each property.

## Recommended Data Types
- bigint for large numeric IDs and counters
- uuid for globally distributed identifiers
- varchar(n) for short text and codes
- text for large free-form content
- boolean for flags
- decimal(p,s) for monetary values
- timestamp with time zone for temporal fields
- jsonb or json for flexible metadata when needed

## Domain Examples
- booking_amount: decimal(12,2)
- currency_code: varchar(3)
- status_code: varchar(30)
- metadata: jsonb
- is_deleted: boolean

## Guidance
- Avoid storing monetary values as floating point types.
- Use constrained text types where possible for codes and enums.
