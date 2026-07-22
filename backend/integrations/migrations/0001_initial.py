from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProviderConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider_name", models.CharField(max_length=100, unique=True)),
                ("provider_type", models.CharField(default="mock", max_length=100)),
                ("endpoint", models.URLField(blank=True)),
                ("api_key", models.CharField(blank=True, max_length=255)),
                ("timeout_seconds", models.PositiveIntegerField(default=10)),
                ("retry_count", models.PositiveIntegerField(default=3)),
                ("enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "provider_configuration"},
        ),
        migrations.CreateModel(
            name="ProviderCallLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider_name", models.CharField(max_length=100)),
                ("operation", models.CharField(max_length=100)),
                ("status", models.CharField(max_length=50)),
                ("response_code", models.CharField(blank=True, max_length=20)),
                ("details", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "provider_call_log"},
        ),
    ]
