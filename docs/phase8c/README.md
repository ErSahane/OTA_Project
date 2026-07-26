# Phase 8C - Search Optimization Engine

## Cache architecture

`SearchResultCache` stores canonical, provider-aggregated result sets under `flight-search:v2:<sha256>`. Its key is a canonical JSON encoding of the validated itinerary, cabin, and passenger request; UI-only filters, sort order, and page do not fragment the cache. Django uses Redis when `USE_REDIS=true` and `REDIS_URL` is configured, otherwise the existing local-memory fallback is used for development.

Set `FLIGHT_SEARCH_CACHE_TTL_SECONDS` (default: 900) to control expiry. Cached results are immutable data supplied to `SearchResultProcessor`, which filters and pages a fresh response safely.

## Search options

Pass options on `POST /api/v1/flight-search/search/` as query parameters:

- `providers` and `airlines`: repeatable filters.
- `min_price`, `max_price`, and `max_stops`.
- `sort`: `price`, `-price`, `duration`, `-duration`, `stops`, or `-stops`.
- `page` (default 1) and `page_size` (default 20, maximum 100).

Responses include `pagination` with page, page size, total result count, and total pages. Swagger documents all parameters at `/api/docs/`.

## Observability

Each response emits a `flight_search.cache` metric tagged hit/miss and calls the provider-independent `SearchAnalyticsHook`. Deployments can replace the no-op hook with OpenTelemetry, StatsD, or a queue-backed analytics publisher.
