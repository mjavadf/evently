# Generated by Django 5.0.1 on 2024-04-08 11:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0022_event_cover_delete_eventimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='name',
        ),
        migrations.AddField(
            model_name='event',
            name='location_type',
            field=models.CharField(choices=[('O', 'Online'), ('V', 'Venue'), ('H', 'Hybrid'), ('U', 'Undecided')], default='U', max_length=1),
        ),
        migrations.AddField(
            model_name='event',
            name='meeting_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='event', to='events.location'),
        ),
    ]
