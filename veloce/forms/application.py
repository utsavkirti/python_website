from django import forms
from django.core import exceptions
from django.contrib.auth.models import User

from veloce import models, enums
from veloce.forms import widgets, base
from . import utils

from datetime import date

AGREEMENT_LABEL = """
    I agree that all the information above is accurate to the best of my knowledge.
"""


class AgreementForm(forms.Form):
    TITLE = ''
    full = ['agreement']

    agreement = forms.BooleanField(
        widget=widgets.CustomCheckbox(label=AGREEMENT_LABEL),
        label=""
    )


class ApplicationStep1Form(base.BaseModelForm):
    TITLE = "Loan Application Details"
    full = ['coborrower_email', 'borrower', 'borrower_email', 'total_emi']
    field_order = ['coborrower_email', 'borrower', 'borrower_email', 'bill_no', 'bill_amount', 'bill_date', 'billing_party_name', 'inquired_by', 'down_payment', 'required_loan_amount', 'dealers_given_finance_scheme', 'emi_on_past_finance', 'current_loan_emi','total_emi']

    coborrower_email = forms.EmailField(
        label="Co-borrower Email (optional)"
    )

    class Meta:
        model = models.ApplicationStep1
        fields = ['borrower_email', 'bill_no', 'bill_amount', 'bill_date', 'billing_party_name', 'inquired_by', 'down_payment', 'required_loan_amount', 'dealers_given_finance_scheme', "emi_on_past_finance", 'current_loan_emi', "total_emi"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        utils.select_option(self)
        self.fields['coborrower_email'].required = False
        self.fields['borrower_email'].required = True
        self.fields['coborrower_email'].initial = self.instance.id

        if self.instance.id is not None and self.instance.coborrower is not None:
            self.fields['coborrower_email'].initial = self.instance.coborrower.email

    def clean(self):
        cleaned = super().clean()

        try:
            cleaned['coborrower'] = User.objects.filter(email=self.cleaned_data.get("coborrower_email")).get()
        except exceptions.ObjectDoesNotExist:
            self.add_error("coborrower_email", "User does not exist.")
        return cleaned

    def save(self, *args, **kwargs):
        out = super().save(*args, **kwargs)
        out.coborrower = self.cleaned_data.get("coborrower")
        return out


class InvoiceStep1Form(base.BaseModelForm):
    TITLE = "Invoice Details"
    full = ['invoice_proof']
    field_order = ['customer_email', 'invoice_amount']

    customer_email = forms.EmailField()

    class Meta:
        model = models.InvoiceStep1
        exclude = [
            "application", "customer"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)
        if self.instance.id is not None:
            self.fields['customer_email'].initial = self.instance.customer.email

    def clean(self):
        cleaned = super().clean()
        invoice_amount = cleaned.get("invoice_amount")
        dowmpay_amount = cleaned.get("downpayment_amount")
        print(dowmpay_amount)
        try:
            print("**********", invoice_amount, dowmpay_amount)
            if int(invoice_amount) > 0:
                if int(dowmpay_amount) > int(invoice_amount):
                    self.add_error("downpayment_amount", "Downpayment amount should not be greater than Invoice amount.")
        except Exception as e:
            pass
        try:
            cleaned['customer'] = User.objects.filter(email=self.cleaned_data.get("customer_email")).get()
        except exceptions.ObjectDoesNotExist:
            self.add_error("customer_email", "User does not exist.")
        return cleaned

    def save(self, *args, **kwargs):
        out = super().save(*args, **kwargs)
        cleaned = super().clean()
        out.customer = cleaned.get('customer')
        return out


class ApplicationStep2Form(base.BaseModelForm):
    TITLE = "Bank Details"
    full = ['aadhar_number', "bank_name"]
    # branch_name = forms.ChoiceField(choices=[('', ''), ('1', 'test')])

    class Meta:
        model = models.ApplicationStep2
        fields = [ "bank_account_number", "ifsc_code", "bank_name", "borrower_bank_account_number", "borrower_ifsc_code", "borrower_bank_name" ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)


FORMS = {
    enums.ApplicationType.INVOICE.value: [
        InvoiceStep1Form,
        ApplicationStep2Form
    ],
    enums.ApplicationType.LOAN.value: [
        ApplicationStep1Form,
        ApplicationStep2Form
    ]
}

