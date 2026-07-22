# Multi-Product Extension Strategy

## Objective
Prepare the architecture for future hotel, bus, visa, and insurance products without major redevelopment.

## Recommended Pattern
- Introduce a common reservation abstraction for booking lifecycle, payments, and customer context.
- Keep product-specific logic isolated behind domain modules.
- Reuse identity, notification, support, audit, and payment services across products.
- Define product-specific inventory, fare rule, and policy entities in separate modules.

## Extension Guidance
- Separate product-specific schemas from the core booking workflow.
- Use adapters for supplier and policy integration.
- Preserve shared governance for payments, security, and auditability.
