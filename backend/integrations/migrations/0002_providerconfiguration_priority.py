from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("integrations", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="providerconfiguration",
            name="priority",
            field=models.PositiveIntegerField(default=100, help_text="Lower values are queried and ranked first."),
        ),
        migrations.AlterModelOptions(
            name="providerconfiguration",
            options={"ordering": ("priority", "provider_name")},
        ),
    ]
