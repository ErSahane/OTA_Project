# Phase 8B - Multi-Provider Aggregation Engine

## Design

`ProviderAggregationService` is the provider-neutral search orchestration boundary. It loads enabled `ProviderConfiguration` records ordered by `priority`, invokes each through the existing `ProviderService` in a bounded thread pool, and returns successful results even when one or more suppliers fail.

Every run has a correlation ID (use `X-Correlation-ID`, or one is generated). The provider adapter receives it in the generic payload. The service emits structured log fields and calls the `integrations.metrics.metrics` hook, which can be replaced by an OpenTelemetry or StatsD implementation without changing orchestration logic.

## Resilience

- Provider priority: lower numeric priority wins a duplicate.
- Retry: bounded exponential backoff, using each provider configuration's `retry_count`.
- Timeout: aggregation waits only through the configured provider deadline; adapters must respect their own `timeout_seconds` for network calls.
- Circuit breaker: three consecutive failed aggregate attempts opens a per-provider cache-backed circuit for 60 seconds (both configurable).
- Partial failure: errors, open circuits, and timed-out providers are returned as outcomes while remaining results are retained.

## Result handling

The generic mapper preserves normalized provider results, adds provider metadata, derives a stable deduplication key from itinerary/fare content, and ranks results by price, stops, duration, then provider priority. No supplier-specific business rules exist in the aggregation service.
