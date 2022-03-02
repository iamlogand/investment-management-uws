import decimal
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone as django_timezone

from .models import *


class PortfolioRenameForm(forms.Form):
    new_name = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        self.unavailable_names = kwargs.pop("unavailable_names")
        super().__init__(*args, **kwargs)

    def clean_new_name(self):
        data = self.cleaned_data["new_name"]
        if data in self.unavailable_names:
            raise ValidationError("That name is taken.")
        return data


class PortfolioDeleteForm(forms.Form):
    name = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        self.correct_name = kwargs.pop("correct_name")
        super().__init__(*args, **kwargs)

    def clean_name(self):
        data = self.cleaned_data["name"]
        if data != self.correct_name:
            raise ValidationError("That's not the correct name.")
        return data


class PortfolioCreateForm(forms.Form):
    new_port = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        self.unavailable_names = kwargs.pop("unavailable_names")
        super().__init__(*args, **kwargs)

        # Suggest a name for the new portfolio
        suggested_name_basic = "My Portfolio"
        count = 1
        while count < 6:
            if count == 1:
                suggested_name = suggested_name_basic
            else:
                suggested_name = "{0} {1}".format(suggested_name_basic, count)
            if suggested_name not in self.unavailable_names:
                self.fields["new_port"].initial = suggested_name
                break
            else:
                count += 1

    def clean_new_port(self):
        data = self.cleaned_data["new_port"]
        if data in self.unavailable_names:
            raise ValidationError("That name is taken.")
        return data


class SelectPlatformForm(forms.Form):
    platform = forms.ChoiceField(choices=[None], widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        self.available_platforms_set = kwargs.pop("available_platforms")
        super().__init__(*args, **kwargs)
        choices = queryset_to_choices(self.available_platforms_set)
        self.fields["platform"].choices = choices


class SelectAccountTypeForm(forms.Form):
    account_type = forms.ChoiceField(choices=[None], widget=forms.RadioSelect)
    platform = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        available_account_types_set = kwargs.pop("available_account_types")
        selected_platform = kwargs.pop("selected_platform")
        super().__init__(*args, **kwargs)
        choices = queryset_to_choices(available_account_types_set)
        self.fields["account_type"].choices = choices
        self.fields["platform"].initial = selected_platform.name


class AccountDeleteForm(forms.Form):
    account = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        account_id = kwargs.pop("account_id")
        super().__init__(*args, **kwargs)
        self.fields["account"].initial = account_id


class EventDeleteForm(forms.Form):
    event = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        event_rank = kwargs.pop("event_rank")
        super().__init__(*args, **kwargs)
        self.fields["event"].initial = event_rank


class CashDepositAddForm(forms.Form):
    amount = forms.FloatField()
    date = forms.DateTimeField(initial=django_timezone.now())

    def __init__(self, *args, **kwargs):
        account = kwargs.pop("investment_account")
        super().__init__(*args, **kwargs)
        self.investment_account = account

    def clean_amount(self):
        data = self.cleaned_data["amount"]

        # Check that the amount is greater than 0.
        if data <= 0:
            raise ValidationError("Cash deposits must be greater than zero.")

        # Check that the amount has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("That amount has too many decimals.")

        return data

    def clean_date(self):
        data = self.cleaned_data["date"]
        return check_event_date(data, investment_account=self.investment_account)


class CashWithdrawalAddForm(forms.Form):
    amount = forms.FloatField()
    date = forms.DateTimeField(initial=django_timezone.now())

    def __init__(self, *args, **kwargs):
        account = kwargs.pop("investment_account")
        super().__init__(*args, **kwargs)
        self.investment_account = account

    def clean_amount(self):
        data = self.cleaned_data["amount"]

        # Check that the amount is greater than 0.
        if data <= 0:
            raise ValidationError("Cash withdrawals must be greater than zero.")

        # Check that the amount has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("That amount has too many decimals.")

        # Check that the amount doesn't exceed the current cash balance.
        current_cash_balance = self.investment_account.get_cash_balance()
        if data > current_cash_balance:
            cash_balance_string = self.investment_account.get_string_cash_balance()
            error_string = "The cash withdrawal amount must not exceed the current cash balance of {0}.".format(cash_balance_string)
            raise ValidationError(error_string)

        return data

    def clean_date(self):
        data = self.cleaned_data["date"]
        return check_event_date(data, investment_account=self.investment_account)


class SecurityPurchaseAddForm(forms.Form):
    security = forms.ChoiceField(choices=[None])
    security_amount = forms.FloatField()
    amount = forms.FloatField()
    date = forms.DateTimeField(initial=django_timezone.now())
    fee = forms.FloatField(initial=0)
    tax = forms.FloatField(initial=0)

    def __init__(self, *args, **kwargs):
        account = kwargs.pop("investment_account")
        self.available_securities = kwargs.pop("available_securities")
        super().__init__(*args, **kwargs)
        self.investment_account = account

        # build a list of securities for the drop down select
        choices = []
        for sec in self.available_securities:
            security_tuple = (sec.ISIN, sec.name)
            choices.append(security_tuple)
        self.fields["security"].choices = choices

    def clean(self):
        cleaned_data = super().clean()

        # Check that fees and taxes don't exceed the total spent.
        total_amount = cleaned_data.get("amount")
        fee = cleaned_data.get("fee")
        tax = cleaned_data.get("tax")
        if fee and tax and total_amount:
            if fee + tax >= total_amount:
                raise ValidationError("The combined amount spent on fees and taxes must be less than the total spent.")

        return cleaned_data

    def clean_date(self):
        data = self.cleaned_data["date"]
        return check_event_date(data, investment_account=self.investment_account)

    def clean_security_amount(self):
        data = self.cleaned_data["security_amount"]
        if data <= 0:
            raise ValidationError("The quantity bought must be greater than zero.")
        return data

    def clean_amount(self):
        data = self.cleaned_data["amount"]

        # Check that the amount is greater than 0.
        if data <= 0:
            raise ValidationError("The total spent must be greater than zero.")

        # Check that the amount has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("That total spent has too many decimals.")

        # Check that the amount doesn't exceed the current cash balance.
        if data > self.investment_account.get_cash_balance():
            cash_balance_string = self.investment_account.get_string_cash_balance()
            error_string = "The total spent must not exceed the current cash balance of {0}.".format(cash_balance_string)
            raise ValidationError(error_string)

        return data

    def clean_fee(self):
        data = self.cleaned_data["fee"]

        # Check that the fee is not negative.
        if data < 0:
            raise ValidationError("The amount spent on fees must not be negative.")

        # Check that the amount has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("The amount spent on fees has too many decimals.")

        return data

    def clean_tax(self):
        data = self.cleaned_data["tax"]

        # Check that the tax is not negative.
        if data < 0:
            raise ValidationError("The amount spent on taxes must not be negative.")

        # Check that the tax has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("The amount spent on taxes has too many decimals.")

        return data


class SecuritySaleAddForm(forms.Form):
    security = forms.ChoiceField(choices=[None])
    security_amount = forms.FloatField()
    amount = forms.FloatField()
    date = forms.DateTimeField(initial=django_timezone.now())
    fee = forms.FloatField(initial=0)
    tax = forms.FloatField(initial=0)

    def __init__(self, *args, **kwargs):
        account = kwargs.pop("investment_account")
        self.available_securities = kwargs.pop("available_securities")
        super().__init__(*args, **kwargs)
        self.investment_account = account

        # build a list of securities for the drop down select
        choices = []
        for sec in self.available_securities:
            security_tuple = (sec.ISIN, sec.name)
            choices.append(security_tuple)
        self.fields["security"].choices = choices

    def clean(self):
        cleaned_data = super().clean()

        # Check that the quantity of shares sold is no more than there are owned
        owned_securities_dict = self.investment_account.get_securities_dict()
        security_amount = cleaned_data.get("security_amount")
        securityISIN = cleaned_data.get("security")
        try:
            owned = owned_securities_dict[securityISIN]["shares_owned"]
        except KeyError:
            raise ValidationError("There are no securities to sell in this investment account.")
        # if owned and securities_amount:
        if security_amount:
            if security_amount > owned:
                sec_name = owned_securities_dict[securityISIN]["security"].name
                error_string = "There are only {} shares of {} available to sell in this investment account.".format(owned, sec_name)
                raise ValidationError(error_string)

        return cleaned_data

    def clean_date(self):
        data = self.cleaned_data["date"]
        return check_event_date(data, investment_account=self.investment_account)

    def clean_security_amount(self):
        data = self.cleaned_data["security_amount"]

        # Check that the quantity sold is greater than 0.
        if data <= 0:
            raise ValidationError("The quantity sold must be greater than zero.")

        return data

    def clean_amount(self):
        data = self.cleaned_data["amount"]

        # Check that the amount is greater than 0.
        if data <= 0:
            raise ValidationError("The amount earned must be greater than zero.")

        # Check that the amount has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("That amount earned has too many decimals.")

        return data

    def clean_fee(self):
        data = self.cleaned_data["fee"]

        # Check that the fee is not negative.
        if data < 0:
            raise ValidationError("The amount spent on fees must not be negative.")

        # Check that the amount has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("The amount spent on fees has too many decimals.")

        return data

    def clean_tax(self):
        data = self.cleaned_data["tax"]

        # Check that the tax is not negative.
        if data < 0:
            raise ValidationError("The amount spent on taxes must not be negative.")

        # Check that the tax has the right number of decimal places.
        decimal_amount = decimal.Decimal(str(data))
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError("The amount spent on taxes has too many decimals.")

        return data


# From a queryset, build a list of tuples, suitable for a form field's 'choices' attribute.
# Note: The entities must have a 'name' field. Assumes data to send is the same as visible choices.
def queryset_to_choices(queryset):
    output_list = []
    for entity in queryset:
        entity_string = entity.name
        entity_tuple = (entity_string, entity_string)
        output_list.append(entity_tuple)
    return output_list


# For cleaning event forms, check that the date is after the last event and not in the future.
def check_event_date(date_data, investment_account):
    # Get the date of the last event if there is one.
    try:
        last_event = investment_account.get_most_recent_event()
    except IndexError:
        return date_data
    previous_date = last_event.date

    # Check that the date is after the last event.
    if date_data < previous_date:
        previous_date_string = date_as_string(previous_date)
        error_string = "This event must take place after the previous event, which took place on: {}".format(
            previous_date_string)
        raise ValidationError(error_string)

    # Check that the date isn't in the future.
    if date_data > django_timezone.now():
        raise ValidationError("This event can't take place in the future.")

    return date_data