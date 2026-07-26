from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from integrations.models import ProviderConfiguration
from master_data.models import Airport, CabinClass, City, Country, StateRegion
from .models import FlightSearchLog
from .serializers import FlightSearchQuerySerializer
from .services import FlightSearchService


class FlightSearchCoreTests(TestCase):
    def setUp(self):
        country = Country.objects.create(code="GBR", name="United Kingdom")
        state = StateRegion.objects.create(country=country, code="LON", name="London")
        city = City.objects.create(state=state, code="LON", name="London")
        Airport.objects.create(city=city, code="LHR", name="Heathrow")
        Airport.objects.create(city=city, code="LGW", name="Gatwick")
        CabinClass.objects.create(code="ECONOMY", name="Economy")
        ProviderConfiguration.objects.create(provider_name="mock-search", provider_type="mock")
        self.client = APIClient()
        self.departure = timezone.localdate() + timedelta(days=1)
        cache.clear()

    def payload(self, **overrides):
        payload = {"trip_type": "one-way", "cabin_class": "economy", "passenger_adults": 1, "passenger_children": 0, "passenger_infants": 0, "segments": [{"origin": "lhr", "destination": "lgw", "departure_date": self.departure.isoformat(), "return_date": None}]}
        payload.update(overrides)
        return payload

    def test_one_way_is_normalized_and_persisted(self):
        serializer = FlightSearchQuerySerializer(data=self.payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        query = serializer.save()
        self.assertEqual(query.cabin_class, "ECONOMY")
        self.assertEqual(query.segments.get().origin, "LHR")

    def test_round_trip_requires_valid_return_date(self):
        serializer = FlightSearchQuerySerializer(data=self.payload(trip_type="round-trip"))
        self.assertFalse(serializer.is_valid())
        payload = self.payload(trip_type="round-trip")
        payload["segments"][0]["return_date"] = (self.departure + timedelta(days=2)).isoformat()
        self.assertTrue(FlightSearchQuerySerializer(data=payload).is_valid())

    def test_multi_city_requires_ordered_segments(self):
        payload = self.payload(trip_type="multi-city", segments=[
            {"origin": "LHR", "destination": "LGW", "departure_date": self.departure.isoformat(), "return_date": None},
            {"origin": "LGW", "destination": "LHR", "departure_date": (self.departure + timedelta(days=1)).isoformat(), "return_date": None},
        ])
        self.assertTrue(FlightSearchQuerySerializer(data=payload).is_valid())

    def test_passenger_and_route_validation(self):
        self.assertFalse(FlightSearchQuerySerializer(data=self.payload(passenger_infants=2)).is_valid())
        invalid = self.payload(segments=[{"origin": "LHR", "destination": "LHR", "departure_date": self.departure.isoformat(), "return_date": None}])
        self.assertFalse(FlightSearchQuerySerializer(data=invalid).is_valid())

    def test_service_logs_and_caches(self):
        serializer = FlightSearchQuerySerializer(data=self.payload())
        serializer.is_valid(raise_exception=True)
        query = serializer.save()
        self.assertFalse(FlightSearchService.search(query)["cached"])
        self.assertTrue(FlightSearchService.search(query)["cached"])
        self.assertEqual(FlightSearchLog.objects.filter(query=query).count(), 1)

    def test_search_endpoint(self):
        response = self.client.post("/api/v1/flight-search/search/", self.payload(), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["provider"], "mock-search")

from time import perf_counter
from unittest.mock import patch

from .optimization import SearchResultCache, SearchResultProcessor


class SearchOptimizationTests(FlightSearchCoreTests):
    def test_filter_sort_and_paginate_results(self):
        results = [
            {"id": "a", "provider": "one", "price": 300, "stops": 1, "duration_minutes": 120, "provider_priority": 2},
            {"id": "b", "provider": "two", "price": 100, "stops": 0, "duration_minutes": 180, "provider_priority": 1},
            {"id": "c", "provider": "one", "price": 200, "stops": 2, "duration_minutes": 90, "provider_priority": 1},
        ]
        page, meta = SearchResultProcessor.process(results, {"providers": ["one"], "max_stops": 1, "sort": "-price", "page": 1, "page_size": 1})
        self.assertEqual([item["id"] for item in page], ["a"])
        self.assertEqual(meta["total_results"], 1)

    def test_cache_key_is_deterministic(self):
        first = {"cabin_class": "ECONOMY", "segments": [{"origin": "LHR"}], "passenger_adults": 1}
        second = {"passenger_adults": 1, "segments": [{"origin": "LHR"}], "cabin_class": "ECONOMY"}
        self.assertEqual(SearchResultCache.key_for(first), SearchResultCache.key_for(second))

    def test_cached_search_avoids_second_aggregation(self):
        serializer = FlightSearchQuerySerializer(data=self.payload())
        serializer.is_valid(raise_exception=True)
        query = serializer.save()
        with patch("flight_search.services.ProviderAggregationService.aggregate_flight_search", return_value={"correlation_id": "bench", "results": [{"id": "f", "price": 100, "provider": "mock"}], "provider_outcomes": []}) as aggregate:
            started = perf_counter()
            first = FlightSearchService.search(query)
            cold_elapsed = perf_counter() - started
            started = perf_counter()
            second = FlightSearchService.search(query)
            warm_elapsed = perf_counter() - started
        self.assertFalse(first["cached"])
        self.assertTrue(second["cached"])
        self.assertEqual(aggregate.call_count, 1)
        self.assertLess(warm_elapsed, max(cold_elapsed * 5, 0.05))
