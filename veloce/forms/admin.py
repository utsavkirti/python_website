from django import forms
from veloce import models
from veloce.forms import widgets, base


class ApplicationRejectForm(base.BaseModelForm):
    TITLE = "Reject Application"
    full = ["reject_reason"]

    class Meta:
        model = models.ReviewedVeloceApplication
        fields = ["reject_reason"]
        widgets = {
            'reject_reason': forms.Textarea()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ApplicationApproveForm(base.BaseModelForm):
    TITLE = "Approve Application"
    full = ["loan_amount", "sanctioned_loan_amount", 'disbursement_amount']

    class Meta:
        model = models.Loan
        fields = ["loan_amount", 'dealer_scheme_roi', 'dealer_scheme_emi', "sanctioned_loan_amount", "interest_rate", "loan_tenure", 'disbursement_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_amount'].widget.attrs = {'readonly': True}
        self.fields['dealer_scheme_roi'].widget.attrs = {'readonly': True}
        self.fields['dealer_scheme_emi'].widget.attrs = {'readonly': True}
        print(self.instance.pk)
        if self.instance.pk:
            self.fields['loan_amount'].widget.attrs = {'disabled': True}
            self.fields['dealer_scheme_roi'].widget.attrs = {'disabled': True}
            self.fields['dealer_scheme_emi'].widget.attrs = {'disabled': True}
            self.fields['sanctioned_loan_amount'].widget.attrs = {'disabled': True}
            self.fields['interest_rate'].widget.attrs = {'disabled': True}
            self.fields['loan_tenure'].widget.attrs = {'disabled': True}
            self.fields['disbursement_amount'].widget.attrs = {'disabled': True}