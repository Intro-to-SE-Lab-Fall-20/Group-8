from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Defines the database object representing a user of this website.
    Nothing for now... simply inherits from base django user model.
    """

    pass


class Email(models.Model):
    """
    Defines the database object representing an email.
    """

    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    recipients = models.ManyToManyField(to='RecipientEmail', related_name='recipient_emails')
    sender = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE, related_name='sender_email')
    body = models.TextField(blank=True, null=True)


class SenderEmail(models.Model):
    """
    Represents the relationship between a Sender (CustomUser) and an Email.
    """

    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE)
    email = models.ForeignKey(to='Email', on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=True)


class RecipientEmail(models.Model):
    """
    Represents the relationship between a Recipient (CustomUser) and an Email.
    """

    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    recipient = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE)
    email = models.ForeignKey(to='Email', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


class Attachment(models.Model):
    """
    Defines the database object representing an email attachment.
    How to handle uploading files in Django: https://stackoverflow.com/a/8542030/10135464
    Django files reference: https://docs.djangoproject.com/en/dev/topics/files/
    """

    FILE = "FILE"
    IMAGE = "IMAGE"
    ATTACH_CHOICES = [
        (FILE, 'File'),
        (IMAGE, 'Image'),
    ]

    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.ForeignKey(to='Email', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ATTACH_CHOICES, default=FILE)
    file = models.FileField(upload_to='uploads/files/%Y/%m/%d/')
    image = models.ImageField(upload_to='uploads/images/%Y/%m/%d/')
