from django.urls import path

from . import views


app_name = 'portfolioapp'
urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("", views.home_redirect_view),
]
