from django.core.exceptions import ValidationError
from django import forms


class PortfolioRenameForm(forms.Form):
    new_name = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        self.unavailable_names = kwargs.pop("unavailable_names")
        super(PortfolioRenameForm, self).__init__(*args, **kwargs)

    def clean_new_name(self):
        data = self.cleaned_data["new_name"]
        if data in self.unavailable_names:
            raise ValidationError("That name is taken.")
        return data


class PortfolioDeleteForm(forms.Form):
    name = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        self.correct_name = kwargs.pop("correct_name")
        super(PortfolioDeleteForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        data = self.cleaned_data["name"]
        if data != self.correct_name:
            raise ValidationError("That's not the correct name.")
        return data


class PortfolioCreateForm(forms.Form):
    new_port = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        self.unavailable_names = kwargs.pop("unavailable_names")
        super(PortfolioCreateForm, self).__init__(*args, **kwargs)

    def clean_new_port(self):
        data = self.cleaned_data["new_port"]
        if data in self.unavailable_names:
            raise ValidationError("That name is taken.")
        return data