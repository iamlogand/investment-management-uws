from django.urls import path

from . import views


app_name = 'portfolioapp'
urlpatterns = [
    path("", views.overview_view, name="overview"),
    path("portfolios/", views.portfolio_list_view, name="portfolio_list"),
    path("portfolios/<str:portfolio_name>/select/", views.portfolio_selector_view, name="portfolio_selector"),
    path("portfolios/<str:portfolio_name>/rename/", views.portfolio_rename_view, name="portfolio_rename"),
    path("portfolios/<str:portfolio_name>/delete/", views.portfolio_delete_view, name="portfolio_delete"),
    path("portfolios/create/", views.portfolio_create_view, name="portfolio_create"),
    path("investment-accounts/add/", views.account_add_view, name="account_add"),
    path("investment-accounts/<str:platform_name>/<str:account_type_name>/", views.account_view,
         name="investment_account"),
    path("investment-accounts/<str:platform_name>/<str:account_type_name>/delete/", views.account_delete_view,
         name="account_delete"),
    path("investment-accounts/<str:platform_name>/<str:account_type_name>/events/<int:event_rank>/", views.event_view,
         name="event"),
    path("investment-accounts/<str:platform_name>/<str:account_type_name>/events/<int:event_rank>/delete/",
         views.event_delete_view, name="event_delete"),
    path("investment-accounts/<str:platform_name>/<str:account_type_name>/events/add-cash-deposit/",
         views.cash_deposit_add_view, name="cash_deposit_add"),
    path("investment-accounts/<str:platform_name>/<str:account_type_name>/events/add-cash-withdrawal/",
         views.cash_withdrawal_add_view, name="cash_withdrawal_add"),
    path("investment-accounts/<str:platform_name>/<str:account_type_name>/events/add-security-purchase/",
         views.security_purchase_add_view, name="security_purchase_add"),
    path("investment-accounts/<str:platform_name>/<str:account_type_name>/events/add-security-sale/",
         views.security_sale_add_view, name="security_sale_add"),
]
