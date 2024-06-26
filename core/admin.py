from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.


#Admin model class for managing users
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    #Fields available to new users when signing on,
    # we are overridding this so that we can include the first name and
    # last name fields.  
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )