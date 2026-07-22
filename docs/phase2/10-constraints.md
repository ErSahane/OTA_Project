# Constraints

## Purpose
Ensure data quality, validity, and predictable business behavior.

## Recommended Constraints
- NOT NULL for mandatory fields
- CHECK constraints for enumerated values and business bounds
- UNIQUE constraints for natural business keys
- FOREIGN KEY constraints for referential integrity

## Example Constraint Rules
- booking status must be one of a controlled set of values
- payment amount must be greater than zero
- email addresses should follow a standard format if stored as structured values
- duplicate active booking references should be prevented where business rules require it

## Governance
- Constraints should be documented and reviewed with domain owners.
- Complex validations that span multiple tables should be enforced in application workflows or service logic where appropriate.
