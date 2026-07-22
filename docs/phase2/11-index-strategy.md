# Index Strategy

## Objectives
Support fast reads, efficient lookups, and scalable query performance.

## Index Principles
- Index primary lookup keys and frequently filtered columns.
- Index foreign keys that are used in joins or filtering.
- Avoid excessive indexing on write-heavy tables.
- Use composite indexes for common query patterns.

## Recommended Indexes
- bookings(status, created_at)
- bookings(customer_id, status)
- booking_items(booking_id, status)
- payments(booking_id, status)
- support_tickets(status, created_at)
- suppliers(code)

## Performance Guidance
- Review indexing strategy after workload profiling.
- Use partial indexes where applicable for active or recent records.
- Maintain index maintenance plans in high-write environments.
