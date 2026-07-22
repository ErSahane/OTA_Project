# Performance Strategy

## Objectives
Maintain low-latency reads and reliable writes as traffic grows to millions of users.

## Performance Principles
- Use indexing for hot-read and join-heavy paths.
- Cache frequently accessed reference data.
- Keep write paths narrow and transactional.
- Avoid overly chatty queries and unnecessary joins in critical flows.

## Recommended Practices
- Denormalize only where access patterns justify it.
- Use read replicas where appropriate for reporting and search workloads.
- Use connection pooling and query tuning as operations maturity grows.
- Benchmark critical queries before and after schema changes.
