from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Email, Sender, Recipient, Attachment

# Register your models here.
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Email, admin.ModelAdmin)
admin.site.register(Sender, admin.ModelAdmin)
admin.site.register(Recipient, admin.ModelAdmin)
admin.site.register(Attachment, admin.ModelAdmin)
