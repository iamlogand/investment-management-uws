from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    def get_selected_portfolio(self):
        try:
            portfolios = Portfolio.objects.filter(owner=self)
            selected_portfolio = portfolios.get(selected=True)
        except Portfolio.DoesNotExist:
            selected_portfolio = None
        return selected_portfolio

    def get_owned_portfolios(self):
        try:
            portfolios = Portfolio.objects.filter(owner=self)
        except Portfolio.DoesNotExist:
            portfolios = None
        return portfolios


class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    selected = models.BooleanField(default=False)
    creation_date = models.DateTimeField()

    @classmethod
    def create(cls, owner, name):
        now = timezone.now()
        portfolio = cls(owner=owner, name=name, creation_date=now)
        return portfolio

    def get_sibling_portfolios(self):
        siblings = Portfolio.objects.filter(owner=self.owner)
        return siblings

    def set_selected(self):
        siblings = self.get_sibling_portfolios()
        for portfolio in siblings:
            portfolio.selected = False
            portfolio.save()
        self.selected = True
        self.save()
