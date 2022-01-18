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

'''
allauth templates and corresponding URLs:

account_inactive.html               /accounts/inactive
email_confirm.html	                /accounts/confirm-email/
login.html	                        /accounts/login/
logout.html	                        /accounts/logout/
password_reset.html	                /accounts/password/reset/
password_reset_done.html	        /accounts/password/reset/done/
password_reset_from_key.html	    /accounts/password/reset/key/<key>/
password_reset_from_key_done.html   /accounts/password/reset/key/done/
signup.html	                        /accounts/signup/
verification_sent.html	            /accounts/confirm-email/
'''