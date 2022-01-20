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

    # Make a list of the user's portfolio names (strings)
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)

    # Create a blank portfolio-rename form in case user wants to rename the selected portfolio
    portfolio_rename_form = PortfolioRenameForm(unavailable_names = owned_portfolio_names)

    # Create a blank portfolio-delete form in case user wants to delete the selected portfolio
    portfolio_delete_form = PortfolioDeleteForm(correct_name = request.user.get_selected_portfolio())

    # Create a blank portfolio-delete form in case user wants to create a new portfolio
    portfolio_create_form = PortfolioCreateForm(unavailable_names = owned_portfolio_names)

    return render(request, "portfolioapp/portfolio_list.html", {
        "portfolio_list": owned_portfolios,
        "portfolio_rename_form": portfolio_rename_form,
        "portfolio_delete_form": portfolio_delete_form,
        "portfolio_create_form": portfolio_create_form,
    })


@login_required
def portfolio_selector_view(request, name):
    owned_portfolios = request.user.get_owned_portfolios()
    try:
        portfolio_to_select = owned_portfolios.get(name=name)
        portfolio_to_select.set_selected()
        return HttpResponseRedirect("/portfolios/")
    except Portfolio.DoesNotExist:
        return custom_404(request)


@login_required
def portfolio_rename_view(request):
    owned_portfolios = request.user.get_owned_portfolios()

    # Make a list of the user's portfolio names (strings)
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)

    if request.method == "POST": # The view is processing a form - normal
        portfolio_rename_form = PortfolioRenameForm(request.POST, unavailable_names=owned_portfolio_names)

        # The form is valid - rename the portfolio then redirect them back to the portfolio page
        if portfolio_rename_form.is_valid():
            new_name = portfolio_rename_form.cleaned_data["new_name"]
            selected_portfolio = request.user.get_selected_portfolio()
            selected_portfolio.name = new_name
            selected_portfolio.save()
            return HttpResponseRedirect("/portfolios/")

        else: # The form is invalid - render the template and the processed form
            return render(request, "portfolioapp/portfolio_list.html",
                          {"portfolio_list": owned_portfolios, "portfolio_rename_form": portfolio_rename_form})

    else: # There is no form - strange... redirect them to the portfolio page
        return HttpResponseRedirect("/portfolios/")


@login_required
def portfolio_delete_view(request):
    owned_portfolios = request.user.get_owned_portfolios()
    selected_portfolio = request.user.get_selected_portfolio()

    # Make a list of the user's portfolio names (strings)
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)

    if request.method == "POST": # The view is processing a form - normal
        selected_portfolio_name = selected_portfolio.name
        portfolio_delete_form = PortfolioDeleteForm(request.POST, correct_name=selected_portfolio_name)

        # The form is valid - delete the portfolio then redirect them back to the portfolio page
        if portfolio_delete_form.is_valid():
            selected_portfolio.delete()
            return HttpResponseRedirect("/portfolios/")

        else: # The form is invalid - render the template and the processed form
            return render(request, "portfolioapp/portfolio_list.html",
                          {"portfolio_list": owned_portfolios, "portfolio_delete_form": portfolio_delete_form})

    else: # There is no form - strange... redirect them to the portfolio page
        return HttpResponseRedirect("/portfolios/")


@login_required
def portfolio_create_view(request):
    owned_portfolios = request.user.get_owned_portfolios()

    # Make a list of the user's portfolio names (strings)
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)

    if request.method == "POST": # The view is processing a form - normal
        portfolio_create_form = PortfolioCreateForm(request.POST, unavailable_names=owned_portfolio_names)

        # The form is valid - delete the portfolio then redirect them back to the portfolio page
        if portfolio_create_form.is_valid():
            name = portfolio_create_form.cleaned_data["new_port"]
            new_portfolio = Portfolio.create(owner=request.user, name=name)
            new_portfolio.save()
            return HttpResponseRedirect("/portfolios/")

        else: # The form is invalid - render the template and the processed form
            return render(request, "portfolioapp/portfolio_list.html",
                          {"portfolio_list": owned_portfolios, "portfolio_create_form": portfolio_create_form})

    else: # There is no form - strange... redirect them to the portfolio page
        return HttpResponseRedirect("/portfolios/")


@login_required
def track_view(request):
    portfolio = request.user.get_selected_portfolio()
    return render(request, "portfolioapp/track.html", {"portfolio": portfolio})


@login_required
def manage_view(request):
    portfolio = request.user.get_selected_portfolio()
    return render(request, "portfolioapp/manage.html", {"portfolio": portfolio})
