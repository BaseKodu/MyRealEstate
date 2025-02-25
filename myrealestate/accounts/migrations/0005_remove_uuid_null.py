# Generated by Django 5.1.3 on 2024-12-07 14:52

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_populate_uuid_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email_verification_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
