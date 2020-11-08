from django.db import migrations, models

from app.models import CustomUser


def update_email(apps, schema_editor):
    """
    Iterates through all current users in DB and updates email.
    """

    for user in CustomUser.objects.all():
        user.email = f"{user.username}@simpleemail.com"

    return


class Migration(migrations.Migration):

    dependencies = [('app', '0001_initial')]

    operations = [
        # migrations.RunPython(update_email)
    ]
