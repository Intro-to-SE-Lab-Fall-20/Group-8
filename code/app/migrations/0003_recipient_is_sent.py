# Generated by Django 3.1.1 on 2020-09-25 16:29

from django.db import migrations, models

from app.models import Recipient


def update_is_sent(apps, schema_editor):
    """
    Updates the 'is_sent' column on all existing recipients to be True.
    """

    for recipient in Recipient.objects.all():
        recipient.is_sent = True
        recipient.save()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200923_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipient',
            name='is_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(update_is_sent)
    ]
