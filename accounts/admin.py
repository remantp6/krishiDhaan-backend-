from django.contrib import admin
from django.contrib.auth.models import Group

from accounts.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    fields = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser',
              'password', 'date_joined', 'last_login',  'role')
    readonly_fields = ('date_joined', 'last_login')

admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
