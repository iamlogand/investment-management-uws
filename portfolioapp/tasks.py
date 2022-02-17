import datetime
from yahoo_fin import stock_info
from django.utils import timezone as django_timezone
from .models import *


def activate_quote_gen():
    try:
        threshold_time = SecurityQuote.objects.order_by("-datetime")[0].datetime + datetime.timedelta(seconds=600)
        if django_timezone.now() > threshold_time:
            generate_quotes()
    except IndexError:
        generate_quotes()


def generate_quotes():
    for security in Security.objects.all():

        # Currently only generates quotes in GBP
        price = stock_info.get_live_price(security.yahoo_id) / 100
        currency = Currency.objects.get(name="pound sterling")
        new_quote = SecurityQuote.create(security=security, currency=currency, price=price)
        new_quote.save()
