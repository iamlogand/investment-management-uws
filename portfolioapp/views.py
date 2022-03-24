from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from portfoliosite.views import custom_404
from portfolioapp.forms import *
from .tasks import refresh_quotes


@login_required
def overview_view(request):

    try:
        portfolio = request.user.get_selected_portfolio()
        return render(request, "portfolioapp/overview.html", {"portfolio": portfolio})
    except Portfolio.DoesNotExist:
        return HttpResponseRedirect("/portfolios/")


@login_required
def portfolio_list_view(request):
    try:
        owned_portfolios = request.user.get_owned_portfolios().order_by('-creation_date')
    except Portfolio.DoesNotExist:
        return custom_404(request)

    # Make a list of the user's portfolio names (strings) and add to context dictionary.
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)
    context_data = {"portfolio_list": owned_portfolios}

    # Create a blank portfolio-rename form in case user wants to rename the selected portfolio.
    try:
        portfolio_rename_form = PortfolioRenameForm(unavailable_names=owned_portfolio_names)
        context_data["portfolio_rename_form"] = portfolio_rename_form
    except Portfolio.DoesNotExist:
        pass

    # Create a blank portfolio-delete form in case user wants to delete the selected portfolio.
    try:
        portfolio_delete_form = PortfolioDeleteForm(correct_name=request.user.get_selected_portfolio())
        context_data["portfolio_delete_form"] = portfolio_delete_form
    except Portfolio.DoesNotExist:
        pass

    # Create a blank portfolio-create form in case user wants to create a new portfolio.
    try:
        portfolio_create_form = PortfolioCreateForm(unavailable_names=owned_portfolio_names)
        context_data["portfolio_create_form"] = portfolio_create_form
    except Portfolio.DoesNotExist:
        pass

    return render(request, "portfolioapp/portfolio_list.html", context_data)


@login_required
def portfolio_selector_view(request, portfolio_name):
    try:
        # Set the portfolio (named in the URL) as selected, and all sibling portfolios as not selected.
        owned_portfolios = request.user.get_owned_portfolios()
        portfolio_to_select = owned_portfolios.get(name=portfolio_name)
        portfolio_to_select.set_selected()
        return HttpResponseRedirect("/portfolios/")
    except Portfolio.DoesNotExist:
        return custom_404(request)


@login_required
def portfolio_rename_view(request, portfolio_name):
    try:
        owned_portfolios = request.user.get_owned_portfolios()
    except Portfolio.DoesNotExist:
        return custom_404(request)

    # Make a list of the user's portfolio names (strings).
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)

    # If the user doesn't own a portfolio by the name given in URL, return a 404.
    if portfolio_name not in owned_portfolio_names:
        return custom_404(request)

    if request.method == "POST":  # The view is processing a form - normal.
        portfolio_rename_form = PortfolioRenameForm(request.POST, unavailable_names=owned_portfolio_names)

        # The form is valid - rename the portfolio then redirect them back to the portfolio page.
        if portfolio_rename_form.is_valid():
            new_name = portfolio_rename_form.cleaned_data["new_name"]
            portfolio_to_rename = owned_portfolios.get(name=portfolio_name)
            portfolio_to_rename.name = new_name
            portfolio_to_rename.save()
            return HttpResponseRedirect("/portfolios/")

        else:  # The form is invalid - render the template and the processed form.
            return render(request, "portfolioapp/portfolio_list.html",
                          {"portfolio_list": owned_portfolios, "portfolio_rename_form": portfolio_rename_form})

    else:  # There is no form - strange... redirect them to the portfolio page.
        return HttpResponseRedirect("/portfolios/")


@login_required
def portfolio_delete_view(request, portfolio_name):
    try:
        owned_portfolios = request.user.get_owned_portfolios()
    except Portfolio.DoesNotExist:
        return custom_404(request)

    #  Make a list of the user's portfolio names (strings).
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)

    # If the user doesn't own a portfolio by the name given in URL, return a 404.
    if portfolio_name not in owned_portfolio_names:
        return custom_404(request)

    if request.method == "POST":  # The view is processing a form - normal.
        portfolio_to_delete = owned_portfolios.get(name=portfolio_name)
        selected_portfolio_name = portfolio_to_delete.name
        portfolio_delete_form = PortfolioDeleteForm(request.POST, correct_name=selected_portfolio_name)

        # The form is valid - delete the portfolio then redirect them back to the portfolio page.
        if portfolio_delete_form.is_valid():
            portfolio_to_delete.delete()
            return HttpResponseRedirect("/portfolios/")

        else:  # The form is invalid - render the template and the processed form.
            return render(request, "portfolioapp/portfolio_list.html",
                          {"portfolio_list": owned_portfolios, "portfolio_delete_form": portfolio_delete_form})

    else:  # There is no form - strange... redirect them to the portfolio page.
        return HttpResponseRedirect("/portfolios/")


@login_required
def portfolio_create_view(request):
    try:
        owned_portfolios = request.user.get_owned_portfolios()
    except Portfolio.DoesNotExist:
        return custom_404(request)

    # Make a list of the user's portfolio names (strings).
    owned_portfolio_names = []
    for p in owned_portfolios:
        owned_portfolio_names.append(p.name)

    if request.method == "POST":  # The view is processing a form - normal.
        portfolio_create_form = PortfolioCreateForm(request.POST, unavailable_names=owned_portfolio_names)

        # The form is valid - delete the portfolio then redirect them back to the portfolio page.
        if portfolio_create_form.is_valid():
            name = portfolio_create_form.cleaned_data["new_port"]
            new_portfolio = Portfolio.create(owner=request.user, name=name)
            new_portfolio.save()
            return HttpResponseRedirect("/portfolios/")

        else:  # The form is invalid - render the template and the processed form.
            return render(request, "portfolioapp/portfolio_list.html",
                          {"portfolio_list": owned_portfolios, "portfolio_create_form": portfolio_create_form})

    else:  # There is no form - strange... redirect them to the portfolio page.
        return HttpResponseRedirect("/portfolios/")


@login_required
def account_add_view(request):
    try:
        portfolio = request.user.get_selected_portfolio()
    except Portfolio.DoesNotExist:
        return HttpResponseRedirect("/portfolios/")

    available_platforms = portfolio.get_avail_platforms()

    if request.method == "POST":  # The view is receiving the results of a form.

        # The view is receiving the results of a select-platform form.
        if ("platform" in request.POST) and ("account_type" not in request.POST):
            select_platform_form = SelectPlatformForm(request.POST, available_platforms=available_platforms)

            # The select-platform form is valid; render the select-account-type template and form. The user will only
            #  be able to select an available account-type belonging to the previously selected platform.
            if select_platform_form.is_valid():
                selected_platform = Platform.objects.get(name=request.POST["platform"])
                available_account_types = portfolio.get_avail_account_types(platform=selected_platform)
                select_account_type_form = SelectAccountTypeForm(available_account_types=available_account_types,
                                                                 selected_platform=selected_platform)
                return render(request, "portfolioapp/new_account/select_account_type.html",
                              {"portfolio": portfolio, "select_account_type_form": select_account_type_form})

            else:  # The select-platform form is invalid; render the template and form again.
                return render(request, "portfolioapp/new_account/select_platform.html",
                              {"portfolio": portfolio, "select_platform_form": select_platform_form})

        # The view is receiving the results of a select-account-type form.
        if ("platform" in request.POST) and ("account_type" in request.POST):
            selected_platform = Platform.objects.get(name=request.POST["platform"])
            available_account_types = portfolio.get_avail_account_types(platform=selected_platform)
            select_account_type_form = SelectAccountTypeForm(request.POST,
                                                             available_account_types=available_account_types,
                                                             selected_platform=selected_platform)

            # The select-account-type form is valid. Create the new investment account and redirect to overview.
            if select_account_type_form.is_valid():
                selected_account_type_name = request.POST["account_type"]
                selected_account_type = InvestmentAccountType.objects.get(name=selected_account_type_name,
                                                                          platform=selected_platform)
                new_investment_account = InvestmentAccount.create(portfolio=portfolio,
                                                                  account_type=selected_account_type)
                new_investment_account.save()
                return HttpResponseRedirect("/")

            else:  # The select-account-type form is invalid; render the template and form again.
                return render(request, "portfolioapp/new_account/select_account_type.html",
                              {"portfolio": portfolio, "select_account_type_form": select_account_type_form})

    # There are no form results for the view to process; start by creating a blank select-platform form
    #  so the user can select a platform to associate with the new account.
    else:
        select_platform_form = SelectPlatformForm(available_platforms=available_platforms)
        return render(request, "portfolioapp/new_account/select_platform.html",
                      {"portfolio": portfolio, "select_platform_form": select_platform_form})


@login_required()
def account_view(request, platform_name, account_type_name):
    try:

        # Find the investment account that matches the user, selected portfolio, platform and account type.
        investment_account = get_investment_account(request.user, platform_name, account_type_name)
        account_id = investment_account.id

        # Potentially refresh security quotes (Celery background task)
        refresh_quotes.delay()


        account_delete_form = AccountDeleteForm(account_id=account_id)
        return render(request, "portfolioapp/account.html", {"account": investment_account,
                                                             "account_delete_form": account_delete_form})

    # If the above methods don't get matches and they error, return a 404.
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)


@login_required()
def account_delete_view(request, platform_name, account_type_name):
    try:
        # Find the investment account that matches the user, selected portfolio, platform and account type.
        investment_account = get_investment_account(request.user, platform_name, account_type_name)
        account_id_from_url = investment_account.id

        # Check the form results and make sure it matches the investment account.
        if request.method == "POST":
            account_id_from_post = request.POST["account"]
            if str(account_id_from_url) == str(account_id_from_post):
                account_delete_form = AccountDeleteForm(request.POST, account_id=account_id_from_post)
                if account_delete_form.is_valid():

                    # Delete the account and return to the overview page.
                    account = InvestmentAccount.objects.get(id=account_id_from_post)
                    account.delete()
                    return HttpResponseRedirect("/")

        # If the request method isn't POST, account IDs don't match, or the form isn't valid, return a 404.
        return custom_404(request)

    # If the referenced portfolio or account doesn't exist, return a 404.
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)


@login_required()
def event_view(request, platform_name, account_type_name, event_rank):
    try:
        # Find the event that matches the user, selected portfolio, platform, account type and rank.
        investment_account = get_investment_account(request.user, platform_name, account_type_name)
        try:
            event = CashFlow.objects.get(account=investment_account, rank=event_rank)
        except CashFlow.DoesNotExist:
            event = SecurityTrade.objects.get(account=investment_account, rank=event_rank)
        event_delete_form = EventDeleteForm(event_rank=event.rank)
        if event.type == "CashFlow":
            return render(request, "portfolioapp/events/cash_flow.html", {"cash_flow": event,
                                                                          "event_delete_form": event_delete_form})
        if event.type == "SecurityTrade":
            return render(request, "portfolioapp/events/security_trade.html", {"security_trade": event,
                                                                               "event_delete_form": event_delete_form})

    # If the referenced portfolio or account doesn't exist, return a 404.
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)


@login_required()
def event_delete_view(request, platform_name, account_type_name, event_rank):
    try:
        # Check the form result rank matches the URL rank.
        if request.method == "POST":
            event_rank_from_post = request.POST["event"]
            if str(event_rank) == str(event_rank_from_post):

                # Find the event that matches the user, selected portfolio, platform, account type and rank.
                investment_account = get_investment_account(request.user, platform_name, account_type_name)
                event = investment_account.get_event(rank=event_rank)

                # Check that the form results are valid.
                event_delete_form = EventDeleteForm(request.POST, event_rank=event_rank)
                if event_delete_form.is_valid():

                    # Delete the event and return to the overview page.
                    event.delete()
                    return HttpResponseRedirect("/investment-accounts/" +
                                                investment_account.account_type.platform.name + "/" +
                                                investment_account.account_type.name + "/")

        # If the request method isn't POST, account IDs don't match, or the form isn't valid, return a 404.
        return custom_404(request)

    # If the referenced portfolio or account doesn't exist, return a 404.
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)


@login_required()
def cash_deposit_add_view(request, platform_name, account_type_name):
    try:
        investment_account = get_investment_account(request.user, platform_name, account_type_name)

        # If there are form results, check that they are valid.
        if request.method == "POST":
            cash_deposit_add_form = CashDepositAddForm(request.POST, investment_account=investment_account)
            if cash_deposit_add_form.is_valid():

                # Form results are valid, so create a new deposit cash flow event.
                amount = float(request.POST["amount"])
                date = request.POST["date"]
                currency = investment_account.account_type.currency
                new_deposit = CashFlow.create(amount=amount, currency=currency,
                                              account=investment_account, date=date)
                new_deposit.save()
                return HttpResponseRedirect("/investment-accounts/" + investment_account.account_type.platform.name
                                            + "/" + investment_account.account_type.name + "/")

            else:  # The results of the form are invalid; render the template and form again.
                return render(request, "portfolioapp/events/cash_deposit_add.html",
                              {"account": investment_account,
                               "cash_deposit_add_form": cash_deposit_add_form})

        # Form hasn't been rendered yet, render the add cash deposit page and a blank form.
        else:
            cash_deposit_add_form = CashDepositAddForm(investment_account=investment_account)
            return render(request, "portfolioapp/events/cash_deposit_add.html",
                          {"account": investment_account,
                          "cash_deposit_add_form": cash_deposit_add_form})

    # If the referenced portfolio or account doesn't exist, return a 404.
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)


@login_required()
def cash_withdrawal_add_view(request, platform_name, account_type_name):
    try:
        investment_account = get_investment_account(request.user, platform_name, account_type_name)

        # If there are form results, check that they are valid.
        if request.method == "POST":
            cash_withdrawal_add_form = CashWithdrawalAddForm(request.POST, investment_account=investment_account)
            if cash_withdrawal_add_form.is_valid():

                # Form results are valid, so create a new withdrawal cash flow event.
                amount = float(request.POST["amount"]) * -1
                date = request.POST["date"]
                currency = investment_account.account_type.currency
                new_withdrawal = CashFlow.create(amount=amount, currency=currency,
                                                 account=investment_account, date=date)
                new_withdrawal.save()
                return HttpResponseRedirect("/investment-accounts/" + investment_account.account_type.platform.name
                                            + "/" + investment_account.account_type.name + "/")

            else:  # The results of the form are invalid; render the template and form again.
                return render(request, "portfolioapp/events/cash_withdrawal_add.html",
                              {"account": investment_account,
                               "cash_withdrawal_add_form": cash_withdrawal_add_form})

        # Form hasn't been rendered yet, render the add cash withdrawal page and a blank form.
        else:
            cash_withdrawal_add_form = CashWithdrawalAddForm(investment_account=investment_account)
            return render(request, "portfolioapp/events/cash_withdrawal_add.html",
                          {"account": investment_account,
                           "cash_withdrawal_add_form": cash_withdrawal_add_form})

    # If the referenced portfolio or account doesn't exist, return a 404.
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)


@login_required()
def security_purchase_add_view(request, platform_name, account_type_name):
    try:
        investment_account = get_investment_account(request.user, platform_name, account_type_name)
        available_securities = Security.objects.all().order_by("name")

        # If there are form results, check that they are valid.
        if request.method == "POST":
            security_purchase_add_form = SecurityPurchaseAddForm(request.POST, investment_account=investment_account,
                                                                 available_securities=available_securities)
            if security_purchase_add_form.is_valid():

                # Form results are valid, so create a new purchase security trade event.
                amount = float(request.POST["amount"]) * -1
                date = request.POST["date"]
                security = Security.objects.get(ISIN=request.POST["security"])
                security_amount = request.POST["security_amount"]
                fee = request.POST["fee"]
                tax = request.POST["tax"]
                currency = investment_account.account_type.currency
                new_purchase = SecurityTrade.create(amount=amount, currency=currency, account=investment_account,
                                                    date=date, security=security, security_amount=security_amount,
                                                    fee=fee, tax=tax)
                new_purchase.save()
                return HttpResponseRedirect("/investment-accounts/" + investment_account.account_type.platform.name
                                            + "/" + investment_account.account_type.name + "/")

            else:  # The results of the form are invalid; render the template and form again.
                return render(request, "portfolioapp/events/security_purchase_add.html",
                              {"account": investment_account,
                               "security_purchase_add_form": security_purchase_add_form})

        # Form hasn't been rendered yet, render the add security purchase page and a blank form.
        else:
            security_purchase_add_form = SecurityPurchaseAddForm(investment_account=investment_account,
                                                                 available_securities=available_securities)
            return render(request, "portfolioapp/events/security_purchase_add.html",
                          {"account": investment_account,
                          "security_purchase_add_form": security_purchase_add_form})

    # If the referenced portfolio or account doesn't exist, return a 404.
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)


@login_required()
def security_sale_add_view(request, platform_name, account_type_name):
    try:
        investment_account = get_investment_account(request.user, platform_name, account_type_name)
        available_securities = investment_account.get_owned_securities()

        # If there are form results, check that they are valid.
        if request.method == "POST":
            security_sale_add_form = SecuritySaleAddForm(request.POST, investment_account=investment_account,
                                                         available_securities=available_securities)
            if security_sale_add_form.is_valid():

                # Form results are valid, so create a new purchase security trade event.
                amount = float(request.POST["amount"])
                date = request.POST["date"]
                security = Security.objects.get(ISIN=request.POST["security"])
                security_amount = float(request.POST["security_amount"]) * -1
                fee = request.POST["fee"]
                tax = request.POST["tax"]
                currency = investment_account.account_type.currency
                new_sale = SecurityTrade.create(amount=amount, currency=currency, account=investment_account, date=date,
                                                security=security, security_amount=security_amount, fee=fee, tax=tax)
                new_sale.save()
                return HttpResponseRedirect("/investment-accounts/" + investment_account.account_type.platform.name
                                            + "/" + investment_account.account_type.name + "/")

            else:  # The results of the form are invalid; render the template and form again.
                return render(request, "portfolioapp/events/security_sale_add.html",
                              {"account": investment_account,
                               "security_sale_add_form": security_sale_add_form})

        # Form hasn't been rendered yet, render the add security purchase page and a blank form.
        else:
            security_sale_add_form = SecuritySaleAddForm(investment_account=investment_account,
                                                         available_securities=available_securities)
            return render(request, "portfolioapp/events/security_sale_add.html",
                          {"account": investment_account,
                          "security_sale_add_form": security_sale_add_form})

    # If the referenced portfolio or account doesn't exist, return a 404.
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)


@login_required()
def owned_security_view(request, platform_name, account_type_name, isin):

    # Find the investment account that matches the user, selected portfolio and platform.
    try:
        investment_account = get_investment_account(request.user, platform_name, account_type_name)
    except (Portfolio.DoesNotExist, Platform.DoesNotExist, InvestmentAccountType.DoesNotExist,
            InvestmentAccount.DoesNotExist):
        return custom_404(request)

    # Find the security in the list of owned securities
    try:
        owned_security = investment_account.get_securities_dict()[isin]
    except KeyError:
        return custom_404(request)

    return render(request, "portfolioapp/new_account/owned_security.html", {"investment_account": investment_account,
                                                                            "owned_security": owned_security})


# Get the investment account
def get_investment_account(user, platform_name, account_type_name):
    portfolio = user.get_selected_portfolio()
    platform = Platform.objects.filter(name=platform_name)
    account_type = InvestmentAccountType.objects.get(platform__in=platform, name=account_type_name)
    investment_account = portfolio.get_investment_accounts().get(account_type=account_type)
    return investment_account
