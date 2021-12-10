from django import forms
from django.core import exceptions
from veloce import validators
from veloce import models
from veloce.forms import widgets, utils
from datetime import date


AGREEMENT_LABEL = """
    I have read, understood and accept the terms and conditions for funding loans on this platform. 
"""


class FundForm(forms.Form):
    full = ['amount', 'agreement_checkbox']

    amount = forms.CharField(
        widget=forms.TextInput(),
        max_length=50,
    )

    agreement_checkbox = forms.BooleanField(
        widget=widgets.CustomCheckbox(label=AGREEMENT_LABEL),
        label=""
    )
