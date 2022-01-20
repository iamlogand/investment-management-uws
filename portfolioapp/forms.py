from django.core.exceptions import ValidationError
from django import forms


class PortfolioRenameForm(forms.Form):
    portfolio_rename_new_name = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        self.unavailable_names = kwargs.pop('unavailable_names')
        super(PortfolioRenameForm, self).__init__(*args, **kwargs)

    def clean_portfolio_rename_new_name(self):
        data = self.cleaned_data['portfolio_rename_new_name']
        if data in self.unavailable_names:
            raise ValidationError("Portfolio names must be unique.")
        return data
