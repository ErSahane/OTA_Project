# Partitioning Recommendations

## Objective
Improve scalability and manageability for large datasets.

## Recommended Partitioning Approaches
- Partition high-volume tables such as bookings, payments, and audit events by time ranges.
- Use monthly or quarterly partitioning for historical data growth.
- Partition by region or business segment where data access patterns justify it.
- Keep recent active data in fast storage and archive older partitions as needed.

## Guardrails
- Partitioning should be introduced only when volume and query patterns demonstrate clear value.
- Avoid over-partitioning small or low-volume tables.
- Keep partition keys aligned with the dominant query patterns.
