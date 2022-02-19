import datetime
from yahoo_fin import stock_info
from celery import shared_task
from django.utils import timezone as django_timezone

from .models import *


@shared_task
def refresh_quotes():

    last_quote_refresh = QuoteManager.objects.get(active=True).last_quote_refresh
    if last_quote_refresh > django_timezone.now() - datetime.timedelta(seconds=10):
        return "Quote refresh denied."

    period = QuoteManager.objects.get(active=True).period

    security_quotes = SecurityQuote.objects.all()
    new_quote_n = 0
    for security in Security.objects.all():
        new_quote_needed = False
        try:
            latest_quote_date = security_quotes.filter(security=security).order_by("-datetime")[0].datetime
            expiry_time = django_timezone.now() - datetime.timedelta(seconds=period)
            if latest_quote_date < expiry_time:
                new_quote_needed = True
        except IndexError:
            new_quote_needed = True

        if new_quote_needed:
            # Currently only generates quotes in GBP
            price = stock_info.get_live_price(security.yahoo_id) / 100
            currency = Currency.objects.get(name="pound sterling")
            new_quote = SecurityQuote.create(security=security, currency=currency, price=price)
            new_quote.save()
            new_quote_n += 1

    updated_quote_manager = QuoteManager.objects.get(active=True)
    updated_quote_manager.last_quote_refresh = django_timezone.now()
    updated_quote_manager.save()
    return "Quote refresh: generated {} new quotes.".format(new_quote_n)

