from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('payment', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='ProcessedWebhook',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('provider', models.CharField(max_length=20)),
                ('event_id', models.CharField(max_length=150, unique=True)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'processed_webhook',
                'ordering': ('-received_at',),
            },
        ),
    ]
