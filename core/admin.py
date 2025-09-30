from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Organization, Client, BonusHistory, MessageTemplate, User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'organization', 'is_staff')
    list_filter = ('organization', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'organization')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'organization'),
        }),
    )

admin.site.register(Organization)
admin.site.register(Client)
admin.site.register(BonusHistory)
admin.site.register(MessageTemplate)
admin.site.register(User, CustomUserAdmin)