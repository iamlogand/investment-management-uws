from django.urls import include, path
from django.contrib import admin
from .views import *


urlpatterns = [
    path('', include('portfolioapp.urls')),

    # URLs for the admin site
    path('admin/', admin.site.urls),

    # Replace some allauth views with 404 responses (effectively removing them from use)
    path('accounts/email/', custom_404),
    path('accounts/password/change/', custom_404),
    path('accounts/password/set/', custom_404),

    # URLs for allauth (login, sign up, verify email, etc.)
    path('accounts/', include('allauth.urls')),
]