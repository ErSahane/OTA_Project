class MetricsHook:
    """Extension point for StatsD, OpenTelemetry, or another metrics backend."""

    def increment(self, name, value=1, tags=None):
        pass

    def timing(self, name, value_ms, tags=None):
        pass


metrics = MetricsHook()
