from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from .custom import *


class User(AbstractUser):

    def get_selected_portfolio(self):
        portfolios = Portfolio.objects.filter(owner=self)
        return portfolios.get(selected=True)

    def get_owned_portfolios(self):
        return Portfolio.objects.filter(owner=self)


class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    selected = models.BooleanField(default=False)
    creation_date = models.DateTimeField()

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, owner, name):
        now = timezone.now()
        portfolio = cls(owner=owner, name=name, creation_date=now)
        return portfolio

    # Returns a queryset containing this portfolio's siblings (other portfolios that share the same owner)
    def get_sibling_portfolios(self):
        siblings = Portfolio.objects.filter(owner=self.owner)
        return siblings

    # Sets the portfolio as selected (selected=True) and sets sibling portfolios as not selected (selected=False)
    def set_selected(self):
        siblings = self.get_sibling_portfolios()
        for portfolio in siblings:
            portfolio.selected = False
            portfolio.save()
        self.selected = True
        self.save()

    # Returns a queryset containing this portfolio's (child) investment accounts
    def get_investment_accounts(self):
        try:
            accounts = InvestmentAccount.objects.filter(portfolio=self)
        except InvestmentAccount.DoesNotExist:
            accounts = None
        return accounts

    # Returns a queryset containing this portfolio's available account types.
    #  The optional 'platform' argument is the platform (instance) to filter results.
    def get_avail_account_types(self, platform=None):
        if platform is None:
            account_types = InvestmentAccountType.objects.all()
        else:
            account_types = InvestmentAccountType.objects.filter(platform=platform)
        child_accounts = self.get_investment_accounts()
        if child_accounts:
            for account in child_accounts:
                account_types = account_types.exclude(name=account.account_type.name)
        return account_types

    # Returns a queryset containing this portfolio's available platforms
    def get_avail_platforms(self):
        all_platforms = Platform.objects.all()
        platforms = all_platforms
        avail_account_types = self.get_avail_account_types()
        for platform in all_platforms:
            child_account_types = platform.get_account_types()
            availability_in_platform = False
            for account_type in child_account_types:
                if account_type in avail_account_types:
                    availability_in_platform = True
                    break
            if not availability_in_platform:
                platforms = platforms.exclude(name=platform.name)
        return platforms

    def get_string_creation_date_time(self):
        return date_as_string(self.creation_date)

    def get_string_creation_date(self):
        return date_as_string(self.creation_date, include_time=False)


class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def get_account_types(self):
        return InvestmentAccountType.objects.filter(platform=self)


class Currency(models.Model):
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=1)
    iso_code = models.CharField(max_length=3)

    class Meta:
        verbose_name_plural = "currencies"

    def __str__(self):
        return self.name


class InvestmentAccountType(models.Model):
    name = models.CharField(max_length=50)  # Note: this does not have to be unique
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.platform) + ": " + self.name


class InvestmentAccount(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    creation_date = models.DateTimeField()
    account_type = models.ForeignKey(InvestmentAccountType, on_delete=models.CASCADE)

    def __str__(self):
        string_out = str(self.portfolio.owner) + ": " + str(self.portfolio) + ": " + str(self.account_type)
        return string_out

    @classmethod
    def create(cls, portfolio, account_type):
        now = timezone.now()
        investment_account = cls(portfolio=portfolio, creation_date=now, account_type=account_type)
        return investment_account

    # Returns a list of events with each entity represented as a dictionary.
    def get_events_list(self):
        events = Event.objects.filter(account=self).values("rank").order_by("-rank")
        list_out = []
        for event in events:
            rank = event["rank"]
            event_ = self.get_event(rank=rank)
            custom_event = {"rank": rank, "date": event_.get_string_date(), "description": event_.get_long_desc(),
                            "type": event_.type}
            list_out.append(custom_event)
        return list_out

    # Returns the most recent event.
    def get_most_recent_event(self):
        event = Event.objects.filter(account=self).order_by("-rank")[0]
        event_ = self.get_event(event.rank)
        return event_

    # From a rank, return the corresponding entity that inherits from "Event" rather than an "Event" entity.
    def get_event(self, rank):
        try:
            event = CashFlow.objects.get(account=self, rank=rank)
        except CashFlow.DoesNotExist:
            event = SecurityTrade.objects.get(account=self, rank=rank)
        return event

    # Returns the cash balance as a number
    def get_cash_balance(self):
        accounting_events = AccountingEvent.objects.filter(account=self)
        balance = 0
        for accounting_event in accounting_events:
            balance += accounting_event.amount
        return balance

    # Returns the cash balance as a string. Plus sign is disabled because cash balance must be positive.
    def get_string_cash_balance(self, plus_sign=False):
        balance = self.get_cash_balance()
        string_out = "{0}{1}{2:.2f}".format(get_number_sign(balance, plus_sign=plus_sign),
                                            self.account_type.currency.symbol, positivise_number(balance))
        return string_out

    # Returns the creation date and time as a string.
    def get_string_creation_date_time(self):
        return date_as_string(self.creation_date)

    # Returns a dictionary where the keys are ISINs and the values are dictionaries like this:
    # "security": Security instance
    # "shares_owned": float of quantity owned
    # "latest_quote": SecurityQuote instance
    def get_owned_securities_dict(self):
        all_events = self.get_events_list()

        sec_event_ranks = []
        for event in all_events:
            if event["type"] == "SecurityTrade":
                sec_event_ranks.append(event["rank"])
        security_events = SecurityTrade.objects.filter(rank__in=sec_event_ranks, account=self)

        sec_amounts_list = {}
        for sec_event in security_events:
            try:
                sec_amounts_list[sec_event.security.ISIN]["shares_owned"] += sec_event.security_amount
            except KeyError:
                sec_amounts_list[sec_event.security.ISIN] = {"shares_owned": sec_event.security_amount,
                                                             "security": sec_event.security}

        non_owned = []
        for sec_ent in sec_amounts_list:
            if sec_amounts_list[sec_ent]["shares_owned"] == 0:
                non_owned.append(sec_ent)
            else:
                int_shares = sec_amounts_list[sec_ent]["shares_owned"]
                if int_shares % 1 == 0:
                    sec_amounts_list[sec_ent]["shares_owned"] = int(int_shares)

        for sec_to_remove in non_owned:
            sec_amounts_list.pop(sec_to_remove)

        for sec_ent in sec_amounts_list:
            latest_quote = sec_amounts_list[sec_ent]["security"].get_latest_quote()
            sec_amounts_list[sec_ent]["latest_quote"] = latest_quote
            sec_amounts_list[sec_ent]["latest_value"] = latest_quote.get_string_value_iso(
                quantity=sec_amounts_list[sec_ent]["shares_owned"])

        return sec_amounts_list

    # Returns a list of ISINs for securities in this investment account.
    def get_owned_securities(self):
        sec_owned_ISINs = list(self.get_owned_securities_dict().keys())
        return Security.objects.filter(ISIN__in=sec_owned_ISINs)

    # Returns a list of securities with each entity represented as a dictionary.
    def get_securities_list(self):
        return list(self.get_owned_securities_dict().values())


class Security(models.Model):
    name = models.CharField(max_length=50)
    ISIN = models.CharField(max_length=12, unique=True)
    yahoo_id = models.CharField(max_length=10, null=True)

    class Meta:
        verbose_name_plural = "securities"

    def __str__(self):
        return self.name

    def get_latest_quote(self):
        try:
            return SecurityQuote.objects.filter(security=self).order_by("-datetime")[0]
        except IndexError:
            raise Exception("Can't find price: " + self.name + " (" + self.ISIN +
                            ") has no related SecurityQuote instances.")


class SecurityQuote(models.Model):
    datetime = models.DateTimeField()
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    price = models.FloatField()

    @classmethod
    def create(cls, security, currency, price):
        now = timezone.now()
        security_quote = cls(datetime=now, security=security, currency=currency, price=price)
        return security_quote

    def get_string_value_iso(self, quantity):
        string_out = "{:.2f} {}".format(self.price * quantity, self.currency.iso_code)
        return string_out

    def get_string_price_iso(self):
        string_out = "{:.4f} {}".format(self.price, self.currency.iso_code)
        return string_out

    def get_string_datetime(self):
        return date_as_string(self.datetime)


# All events inherit from this class
class Event(models.Model):
    rank = models.IntegerField()
    date = models.DateTimeField()
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE)
    type = None

    def get_string_date(self):
        return date_as_string(self.date, include_time=False)

    def get_string_date_time(self):
        return date_as_string(self.date)


# Accounting events, with an associated amount and currency, inherit from this class.
class AccountingEvent(Event):
    amount = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    # Returns positivised amount as a string, example: "100.00".
    def get_string_positivised_amount(self):
        number = positivise_number(self.amount)
        amount_string = "{0:.2f}".format(number)
        return amount_string

    # Returns positivised amount as a string, example: "100.00 GBP".
    # Returns positivised amount as a string, example: "100.00 GBP".
    def get_string_positivised_amount_iso(self):
        string_out = self.get_string_positivised_amount() + " " + self.currency.iso_code
        return string_out


# Deposits and withdrawals are 'cash flows', with positive amounts counting as deposits and negatives as withdrawals.
class CashFlow(AccountingEvent):
    type = "CashFlow"

    @classmethod
    def create(cls, amount, currency, account, date):
        try:
            rank = account.get_most_recent_event().rank + 1
        except IndexError:
            rank = 1
        cash_flow = cls(amount=amount, currency=currency, date=date, rank=rank, account=account)
        return cash_flow

    # Returns string, example: "deposit"
    def get_short_desc(self):
        if self.amount > 0:
            string_out = "deposit"
        else:
            string_out = "withdrawal"
        return string_out

    # Returns string, example: "cash deposit"
    def get_medium_desc(self):
        return "cash " + self.get_short_desc()

    # Returns string, example: "cash deposit of 100 GBP"
    def get_long_desc(self):
        string_out = self.get_medium_desc() + " of "
        string_out += self.get_string_positivised_amount_iso()
        return string_out


# SecurityTrades are security buy and sell events. For buys, amount will be negative
class SecurityTrade(AccountingEvent):
    type = "SecurityTrade"
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    security_amount = models.FloatField()
    fee = models.FloatField()
    tax = models.FloatField()

    @classmethod
    def create(cls, amount, currency, account, date, security, security_amount, fee, tax):
        try:
            rank = account.get_most_recent_event().rank + 1
        except ValueError:
            rank = 1
        security_trade = cls(amount=amount, currency=currency, date=date, rank=rank, account=account, security=security,
                             security_amount=security_amount, fee=fee, tax=tax)
        return security_trade

    # Returns string, example: "sale".
    def get_short_desc(self):
        if self.amount > 0:
            string_out = "security sale"
        else:
            string_out = "security purchase"
        return string_out

    # Returns string, example: "sale of 5 shares of Tesco Plc".
    def get_medium_desc(self):
        security_amount = str(self.get_positivised_security_amount())
        if security_amount == "1":
            plural = ""
        else:
            plural = "s"
        return "{0} of {1} share{2} of {3}".format(self.get_short_desc()[9:], security_amount, plural,
                                                   self.security.name)

    # Returns string, example: "sale of 5 shares of Tesco Plc for 9.80 GBP".
    def get_long_desc(self):
        string_out = self.get_medium_desc() + " for "
        string_out += self.get_string_positivised_amount_iso()
        return string_out

    # Returns security amount (shares) as a positive string.
    def get_positivised_security_amount(self):
        if self.security_amount % 1 == 0:
            units = int(self.security_amount)
        else:
            units = self.security_amount
        if self.security_amount < 0:
            units *= -1
        return units

    # Returns the fee as a string.
    def get_string_fee(self):
        fee_amount_string = "{0:.2f}".format(self.fee)
        return fee_amount_string

    # Returns the tax as a string.
    def get_string_tax(self):
        tax_amount_string = "{0:.2f}".format(self.tax)
        return tax_amount_string
