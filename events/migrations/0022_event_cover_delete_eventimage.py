# Generated by Django 5.0.1 on 2024-03-18 14:18

import events.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_event_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to='events/covers', validators=[events.validators.validate_image_size]),
        ),
        migrations.DeleteModel(
            name='EventImage',
        ),
    ]