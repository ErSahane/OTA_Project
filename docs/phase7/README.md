# Phase 7 – Master Data Management

## Overview
This phase adds a reusable master data module for the OTA platform, covering countries, states/regions, cities, airports, airlines, currencies, languages, cabin classes, passenger types, trip types, and fare types.

## Implemented capabilities
- Shared master data models with soft-delete support and audit timestamps
- CRUD APIs with search, ordering, and pagination
- Admin registration for all master data entities
- Import/export framework for CSV-based bulk management
- Unit tests for core CRUD and soft-delete behavior

## Notes
- The module is designed to be reused by booking, pricing, and operational services.
- Endpoint URLs are exposed under /api/master-data/.
