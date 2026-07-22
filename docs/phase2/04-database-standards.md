# Database Standards

## Core Principles
- Use a relational model for transactional integrity.
- Separate operational, analytical, and audit data where needed.
- Prefer explicit schemas and constrained relationships.
- Treat data quality and traceability as first-class requirements.

## Standard Design Rules
- Primary keys should be stable and non-guessable.
- Every table should have audit fields for traceability.
- Soft delete should be the default for business data.
- Avoid nullable fields for mandatory business semantics.
- Use enums or lookup tables for controlled domain values.

## Data Lifecycle Rules
- Historical records should not be overwritten.
- Business state transitions should be auditable.
- Integration and import data should be isolated from transactional business data.
