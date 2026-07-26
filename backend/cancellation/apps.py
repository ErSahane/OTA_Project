from django.apps import AppConfig


class CancellationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cancellation"
    label = "cancellation"

    def ready(self):
        import cancellation.signals  # noqa: F401
