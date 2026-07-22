# Audit Fields

## Purpose
Enable traceability, security review, and operational debugging.

## Standard Audit Columns
- created_at
- created_by
- updated_at
- updated_by
- deleted_at
- deleted_by
- version

## Usage Rules
- Every core table should have created and updated timestamps.
- Sensitive operations should record actor identity where available.
- Audit fields should be maintained by the application or service layer.

## Traceability Goals
- Understand who created or updated a record.
- Reconstruct sequence of critical business events.
- Support incident investigation and compliance workflows.
