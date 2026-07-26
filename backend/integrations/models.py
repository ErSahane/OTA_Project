from django.db import models


class ProviderConfiguration(models.Model):
    provider_name = models.CharField(max_length=100, unique=True)
    provider_type = models.CharField(max_length=100, default="mock")
    endpoint = models.URLField(blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    priority = models.PositiveIntegerField(default=100, help_text="Lower values are queried and ranked first.")
    timeout_seconds = models.PositiveIntegerField(default=10)
    retry_count = models.PositiveIntegerField(default=3)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "provider_configuration"
        ordering = ("priority", "provider_name")

    def __str__(self):
        return self.provider_name


class ProviderCallLog(models.Model):
    provider_name = models.CharField(max_length=100)
    operation = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    response_code = models.CharField(max_length=20, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "provider_call_log"
