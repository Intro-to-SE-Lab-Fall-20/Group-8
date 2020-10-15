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

    default_subject = 'bbc1ca1f-9f31-4c59-9c12-6af7f3c4b2eb'

    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    body = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=False, default=default_subject)

    def __str__(self):
        return f"{self.subject}: {self.body}"


class Sender(models.Model):
    """
    Represents the relationship between a Sender (CustomUser) and an Email.
    """

    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE)
    email = models.ForeignKey(to='Email', on_delete=models.CASCADE, related_name='sender_email')
    is_draft = models.BooleanField(default=True)
    is_forward = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"


class Recipient(models.Model):
    """
    Represents the relationship between a Recipient (CustomUser) and an Email.
    """

    uid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE)
    email = models.ForeignKey(to='Email', on_delete=models.CASCADE)
    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_forward = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"


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
