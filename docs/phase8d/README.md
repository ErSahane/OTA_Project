# Phase 8D - Fare Rules & Pricing Engine

`POST /api/v1/pricing/quote/` calculates a provider-neutral OTA quote from normalized fare input. The engine evaluates fare family, fare basis, refund, cancellation, date change, baggage, ancillary, tax, service fee, markup, discount, promo, seat, and currency rules without embedding provider-specific logic.

## Design

- `FarePolicy` stores fare-rule and policy behavior.
- `PricingAdjustment` stores reusable tax, markup, service fee, discount, and promo rules.
- `PricingEngine` computes totals and breakdown lines.
- `FareRulesEngine` emits normalized policy output for future multi-provider mapping.

Swagger is available at `/api/docs/`.
