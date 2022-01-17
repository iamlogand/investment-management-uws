from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path('', include('portfolioapp.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
]
