from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FarePolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True)),
                ("fare_family", models.CharField(max_length=100)),
                ("fare_basis", models.CharField(blank=True, max_length=50)),
                ("currency", models.CharField(max_length=3)),
                ("refundable", models.BooleanField(default=False)),
                ("cancellation_allowed", models.BooleanField(default=False)),
                ("date_change_allowed", models.BooleanField(default=False)),
                ("cancellation_penalty", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("date_change_penalty", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("baggage_rules", models.JSONField(blank=True, default=dict)),
                ("refund_rules", models.JSONField(blank=True, default=dict)),
                ("ancillary_rules", models.JSONField(blank=True, default=dict)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "pricing_fare_policy"},
        ),
        migrations.CreateModel(
            name="PricingAdjustment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("adjustment_type", models.CharField(choices=[("tax", "Tax"), ("markup", "Markup"), ("service_fee", "Service fee"), ("discount", "Discount"), ("promo", "Promo")], max_length=20)),
                ("amount_type", models.CharField(choices=[("percentage", "Percentage"), ("fixed", "Fixed")], max_length=20)),
                ("amount", models.DecimalField(decimal_places=4, max_digits=12)),
                ("currency", models.CharField(blank=True, max_length=3)),
                ("promo_code", models.CharField(blank=True, max_length=50)),
                ("priority", models.PositiveIntegerField(default=100)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "pricing_adjustment", "ordering": ("priority", "code")},
        ),
    ]
