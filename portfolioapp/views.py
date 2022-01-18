from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "portfolioapp/home.html"


def home_redirect_view(request):
    return redirect("/home/")


