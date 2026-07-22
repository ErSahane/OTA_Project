# Timestamp Standards

## Objective
Ensure consistent temporal semantics across services and data stores.

## Standard Timestamp Fields
- created_at: record creation time
- updated_at: last modification time
- deleted_at: logical deletion time
- booked_at: domain-specific event time
- confirmed_at: booking confirmation time

## Rules
- Use UTC timestamps for storage.
- Prefer ISO 8601-compatible representations in APIs.
- Avoid local-time storage in business records.
- Use timezone-aware handling in reporting and analytics contexts.
