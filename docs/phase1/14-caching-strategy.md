# Caching Strategy

## Objectives
Improve latency and reduce load on primary data stores for frequently requested data.

## Caching Layers
- Edge caching for public content and static assets
- Distributed cache for session and lookup data
- Application cache for hot-read paths
- Database query result cache where appropriate

## Cache Design Rules
- Cache only data with predictable invalidation patterns
- Use TTLs that balance freshness and performance
- Invalidate on write or use event-driven refresh patterns
- Avoid caching sensitive or highly dynamic transactional data without safeguards

## Candidate Cache Data
- Flight search result summaries
- Fare rules and lookup tables
- User profile and session metadata
- Configuration data and feature flags
