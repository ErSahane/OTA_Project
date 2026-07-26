# Phase 8A - Flight Search Core

`POST /api/v1/flight-search/search/` supports `one-way`, `round-trip`, and `multi-city` requests. It validates active master-data location and cabin codes, itinerary-specific dates, and passenger totals.

The service uses the existing `integrations.services.ProviderService` to fan out to all enabled providers without provider-specific logic. Each provider attempt is persisted in `flight_search_log`; response data is cached for 15 minutes (override with `FLIGHT_SEARCH_CACHE_TIMEOUT`). Every search is kept as history for the authenticated user.

Swagger UI: `/api/docs/`. OpenAPI schema: `/api/schema/`.
