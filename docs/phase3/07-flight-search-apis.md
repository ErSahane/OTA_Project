# Flight Search APIs

## Endpoints
### Search Flights
- POST /api/v1/flight-search/search

### Search Summary
- GET /api/v1/flight-search/summaries

### Fare Rules
- GET /api/v1/flight-search/{searchId}/fare-rules

## Request Considerations
- Origin, destination, departure date, return date, cabin class, passenger count, trip type.

## Response Considerations
- Include itinerary options, pricing, baggage rules, and supplier metadata.

## Notes
- Search APIs should be optimized for low latency and cached where appropriate.
- Supplier fan-out should be abstracted behind the search service contract.
