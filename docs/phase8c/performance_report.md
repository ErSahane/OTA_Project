# Phase 8C Performance Report

## Benchmark coverage

The test suite verifies deterministic cache keys, canonical-result filtering/sorting/pagination, and that a warm identical search bypasses provider aggregation entirely. It measures cold and warm in-process request paths without a brittle absolute latency threshold.

## Operational expectation

A warm cache hit performs no provider fan-out and no provider search logging. Production cache latency and throughput should be measured using the deployed Redis topology, provider count, payload size, and regional network conditions. Track `flight_search.cache` hit/miss metrics and provider aggregation timings together when setting the TTL.

## Run

```powershell
python .\manage.py test flight_search integrations -v 1
```
