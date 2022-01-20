from django.urls import path

from . import views


app_name = 'portfolioapp'
urlpatterns = [
    path("home/", views.home_view, name="home"),
    path("", views.home_redirect_view),
    path("portfolios/", views.portfolio_list_view, name="portfolio_list"),
    path("portfolios/<str:name>/select/", views.portfolio_selector_view, name="portfolio_selector"),
    path("portfolios/rename/", views.portfolio_rename_view, name="portfolio_rename"),
    path("portfolios/delete/", views.portfolio_delete_view, name="portfolio_delete"),
    path("portfolios/create/", views.portfolio_create_view, name="portfolio_create"),
    path("track/", views.track_view, name="track"),
    path("manage/", views.manage_view, name="manage"),
]
