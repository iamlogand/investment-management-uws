from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import admin

from portfolioapp.models import User, Portfolio


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'is_staff', 'last_login')
    search_fields = ('email',)
    ordering = ('email',)


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "creation_date","selected")


admin.site.register(Portfolio, PortfolioAdmin)
