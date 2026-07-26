"""Cache-backed, provider-neutral circuit breaker."""

from dataclasses import dataclass
from django.core.cache import cache


@dataclass(frozen=True)
class CircuitState:
    failures: int = 0
    open: bool = False


class ProviderCircuitBreaker:
    def __init__(self, provider_name, failure_threshold=3, recovery_timeout=60):
        self.key = f"provider-circuit:v1:{provider_name}"
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

    def allow_request(self):
        return not cache.get(self.key, {}).get("open", False)

    def record_success(self):
        cache.delete(self.key)

    def record_failure(self):
        state = cache.get(self.key, {"failures": 0})
        failures = state["failures"] + 1
        if failures >= self.failure_threshold:
            cache.set(self.key, {"failures": failures, "open": True}, self.recovery_timeout)
        else:
            cache.set(self.key, {"failures": failures, "open": False}, self.recovery_timeout)
