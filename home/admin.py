from django.contrib import admin

from home.models import Email, UserEmail

# Register your models here.
admin.site.register(Email)
admin.site.register(UserEmail)
