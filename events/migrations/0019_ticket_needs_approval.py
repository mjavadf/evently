# Generated by Django 5.0.1 on 2024-02-05 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_reservation_qrcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='needs_approval',
            field=models.BooleanField(default=False),
        ),
    ]