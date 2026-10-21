from django.contrib import admin
from .models import AuthUserModel

# Register your models here.
class UserAmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_customer')

admin.site.register(AuthUserModel, UserAmin)