from django.contrib import admin
from accounts.models import LoggedInUser


admin.site.register(LoggedInUser)