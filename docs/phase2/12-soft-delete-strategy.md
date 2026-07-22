# Soft Delete Strategy

## Objective
Preserve historical integrity while allowing business-level logical deletion.

## Recommended Pattern
- Add a boolean column such as is_deleted to each core business table.
- Add a deleted_at timestamp when a record is logically deleted.
- Exclude deleted records by default in normal business queries.
- Preserve deleted records in history and audit views where required.

## Business Rules
- Soft delete should be applied to customer, booking, payment, and support data.
- Hard delete should be reserved for sensitive data cleanup or compliance-driven removal.

## Operational Guidance
- Keep soft delete behavior consistent across services and APIs.
- Ensure deleted records are not reactivated without explicit business review.
