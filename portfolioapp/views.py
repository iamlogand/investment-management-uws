from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from portfolioapp.models import Portfolio
from portfoliosite.views import custom_404
from portfolioapp.forms import *


@login_required
def home_view(request):
    portfolio = request.user.get_selected_portfolio()
    return render(request, "portfolioapp/home.html", {"portfolio": portfolio})


def home_redirect_view(request):
    return HttpResponseRedirect("/home/")


@login_required
def portfolio_list_view(request):
    owned_portfolios = request.user.get_owned_portfolios().order_by('-creation_date')
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)
    if request.method == "POST": # The page is receiving a completed form

        if "portfolio_rename_new_name" in request.POST: # The page is receiving a portfolio rename form
            portfolio_rename_form = PortfolioRenameForm(request.POST, unavailable_names=owned_portfolio_names)
            if portfolio_rename_form.is_valid():
                new_name = portfolio_rename_form.cleaned_data["portfolio_rename_new_name"]
                selected_portfolio = request.user.get_selected_portfolio()
                selected_portfolio.name = new_name
                selected_portfolio.save()
                return HttpResponseRedirect("/portfolios/")
            else:
                return render(request, "portfolioapp/portfolio_list.html", {
                    "portfolio_list": owned_portfolios,
                    "portfolio_rename_form": portfolio_rename_form,
                })
    else: # The page is not receiving a form
        portfolio_rename_form = PortfolioRenameForm(unavailable_names = owned_portfolio_names)
        return render(request, "portfolioapp/portfolio_list.html", {
            "portfolio_list": owned_portfolios,
            "portfolio_rename_form": portfolio_rename_form,
        })


@login_required
def portfolio_selector(request, name):
    owned_portfolios = request.user.get_owned_portfolios()
    try:
        portfolio_to_select = owned_portfolios.get(name=name)
        portfolio_to_select.set_selected()
        return HttpResponseRedirect("/portfolios/")
    except Portfolio.DoesNotExist:
        return custom_404(request)


@login_required
def track_view(request):
    portfolio = request.user.get_selected_portfolio()
    return render(request, "portfolioapp/track.html", {"portfolio": portfolio})


@login_required
def manage_view(request):
    portfolio = request.user.get_selected_portfolio()
    return render(request, "portfolioapp/manage.html", {"portfolio": portfolio})
