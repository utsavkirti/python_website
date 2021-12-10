from django import forms
from django.core import exceptions

from veloce import validators
from veloce import models
from veloce.forms import widgets
from veloce.forms import utils
from veloce.forms.exceptions import SkipStep
from veloce import enums
from datetime import date


class GeneralInfoForm(forms.ModelForm):
    TITLE = 'General Information'

    full = []

    class Meta:
        model = models.GeneralInfo
        exclude = ["veloce_user", ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)

    def set_params(self, obj):
        pass


class EmploymentInfoForm(forms.ModelForm):
    TITLE = 'Employment Information'

    full = []

    class Meta:
        model = models.EmploymentInfo
        exclude = ["veloce_user", ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)

    def set_params(self, obj):
        pass


class InstitutionalInfoForm(forms.ModelForm):
    TITLE = 'General Information'

    full = ['company_name', 'pan_number', 'gst_number',
            'gst_proof', 'pan_card_proof', 'firm_pan']

    class Meta:
        model = models.InstitutionInfo
        exclude = ["veloce_user", ]
        widgets = {
            'gst_proof': widgets.CustomFileInput,
            'pan_card_proof': widgets.CustomFileInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)

    def set_params(self, obj):
        pass


class CurrentAddressForm(forms.ModelForm):
    TITLE = 'Current Address'

    full = ['proof', 'street_address']

    class Meta:
        model = models.Address
        exclude = ["veloce_user", "address_type"]
        widgets = {
            'proof': widgets.CustomFileInput,
            'city': forms.Select(choices=[('', 'Select')]),
            'effective_since': forms.SelectDateWidget(
                years=range(1920, date.today().year),
                empty_label='', attrs={'class': 'datewidget'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)
        if self.instance and self.instance.city:
            self.fields['city'].widget.choices = [
                (self.instance.city, self.instance.city)
            ]

    def set_params(self, obj):
        obj.address_type = enums.AddressType.CURRENT.value


class PermanentAddressForm(forms.ModelForm):
    TITLE = 'Permanent Address'

    full = ['same_as_current_address', 'proof', 'street_address']
    hidden = ['same_as_current_address']
    same_as_current_address = forms.BooleanField(
        widget=widgets.CustomCheckbox(
            label="My permanent address is the same as my current address.",
        ),
        label='',
        required=False
    )

    class Meta:
        model = models.Address
        exclude = ["veloce_user", "address_type"]
        widgets = {
            'proof': widgets.CustomFileInput,
            'city': forms.Select(choices=[('', 'Select')]),
            'effective_since': forms.SelectDateWidget(
                years=range(1920, date.today().year),
                empty_label='', attrs={'class': 'datewidget'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['same_as_current_address']:
            raise SkipStep
        return cleaned_data

    def set_params(self, obj):
        obj.address_type = enums.AddressType.PERMANENT.value


class KycDocumentsForm(forms.ModelForm):
    TITLE = 'KYC Documents'

    full = ["aadhar_number", "aadhar_card", "pan_number", "pan_card"]

    class Meta:
        model = models.KycDocuments
        exclude = ["veloce_user", ]
        widgets = {
            'aadhar_card': widgets.CustomFileInput,
            'pan_card': widgets.CustomFileInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)

    def set_params(self, obj):
        pass


individual_borrower_forms = {
    1: GeneralInfoForm,
    2: EmploymentInfoForm,
    3: CurrentAddressForm,
    4: PermanentAddressForm,
    5: KycDocumentsForm,
}

individual_lender_forms = {
    1: CurrentAddressForm,
    2: PermanentAddressForm,
    3: KycDocumentsForm,
}

institutional_lender_forms = {
    1: InstitutionalInfoForm,
    2: CurrentAddressForm,
}


def get_profile_forms(account_type):
    if enums.AccountType.INDIVIDUAL_BORROWER.value == account_type:
        return individual_borrower_forms
    if enums.AccountType.INDIVIDUAL_LENDER.value == account_type:
        return individual_lender_forms
    if enums.AccountType.INSTITUTIONAL_LENDER.value == account_type:
        return institutional_lender_forms


def get_profile_form(user, step):
    profile_forms = get_profile_forms(user.veloceuser.account_type)
    return profile_forms[step]
