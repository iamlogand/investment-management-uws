from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import admin

from portfolioapp.models import *


class PortfolioInline(admin.TabularInline):
    model = Portfolio
    show_change_link = True


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Define admin model for custom User model with no email field

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

    inlines = [PortfolioInline]


class InvestmentAccountInline(admin.TabularInline):
    model = InvestmentAccount
    show_change_link = True
    readonly_fields = ("platform",)
    fields = ("account_type", "platform", "creation_date")

    @admin.display()
    def platform(self, obj):
        return obj.account_type.platform


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "creation_date", "selected")
    inlines = [InvestmentAccountInline]


@admin.register(InvestmentAccount)
class InvestmentAccountAdmin(admin.ModelAdmin):

    list_display = ("account_type", "platform", "portfolio", "owner", "creation_date")

    @admin.display()
    def platform(self, obj):
        return obj.account_type.platform

    @admin.display()
    def owner(self, obj):
        return obj.portfolio.owner


class InvestmentAccountTypeInline(admin.TabularInline):
    model = InvestmentAccountType


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    inlines = [InvestmentAccountTypeInline]


@admin.register(InvestmentAccountType)
class InvestmentAccountTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "platform", "currency")


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "iso_code")


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = ("name", "ISIN", "yahoo_id")


@admin.register(SecurityQuote)
class SecurityTradeAdmin(admin.ModelAdmin):
    list_display = ("datetime", "security", "currency", "price")


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ("rank","currency", "amount", "date", "account")


@admin.register(SecurityTrade)
class SecurityTradeAdmin(admin.ModelAdmin):
    list_display = ("rank", "currency", "amount", "security", "security_amount", "date", "account")
