# Generated by Django 4.2.2 on 2023-07-01 12:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0008_remove_category_slug_remove_event_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='ticket',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='events.ticket'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='registration',
            name='payment_method',
            field=models.CharField(choices=[('C', 'Credit Card'), ('P', 'PayPal'), ('N', 'Not Required')], default='N', max_length=1),
        ),
        migrations.AlterField(
            model_name='registration',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected'), ('W', 'Wait listed')], default='N', max_length=1),
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together={('ticket', 'participant')},
        ),
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together={('event', 'title')},
        ),
        migrations.RemoveField(
            model_name='registration',
            name='event',
        ),
    ]