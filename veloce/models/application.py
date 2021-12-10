import uuid
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.contrib.auth.models import User
from veloce import validators
from veloce import enums
from veloce.models.helpers import UploadPath


class VeloceApplication(models.Model):
    user = models.ForeignKey(User, related_name="application_by", on_delete=models.CASCADE)
    application_type = models.SmallIntegerField(
        choices=enums.to_choices(enums.ApplicationType),
        default=1
    )
    inquiry_id = models.IntegerField(null=True, blank=True, unique=True)
    is_reviewed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    rejected_by = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    reject_reason = models.TextField(default='', blank=True)
    current_step = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def completion(self):
        return str((self.current_step - 1) * 100 // len(MODELS[self.application_type])) + "%"

    def reject(self, reject_reason, user):
        print("VeloceApplication")
        self.is_approved = False
        self.is_reviewed = True
        self.rejected_by = user
        self.reject_reason = reject_reason
        self.save()

    def approve(self):
        self.is_approved = True
        self.save()

    def reason(self):
        if self.application_type == enums.ApplicationType.INVOICE.value:
            return "Discounted Invoice"
        else:
            return "Loan Reason Hide"
            # return enums.human_readable(enums.LoanReason(self.applicationstep1.loan_reason).name)

    @property
    def coborrower(self):
        if self.application_type == enums.ApplicationType.INVOICE.value:
            return self.invoicestep1.customer
        elif self.applicationstep1.coborrower:
            return self.applicationstep1.coborrower
        return None

    @property
    def coborrower_title(self):
        if self.application_type == enums.ApplicationType.INVOICE.value:
            return "Customer"
        elif self.applicationstep1.coborrower:
            return "Co-borrower"
        return None

    @property
    def user_title(self):
        if self.application_type == enums.ApplicationType.INVOICE.value:
            return "Dealer"
        elif self.applicationstep1.coborrower:
            return "Borrower"
        return None

    def __str__(self):
        return '%s' % self.id

    class Meta:
        unique_together = ('id', 'inquiry_id')


class ReviewedVeloceApplication(models.Model):
    veloce_app = models.ForeignKey(VeloceApplication, on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey(User, related_name="approved_by", null=True, blank=True, on_delete=models.SET_NULL)
    is_reviewed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    rejected_by = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    reject_reason = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def reject(self, reject_reason, user):
        self.is_approved = False
        self.is_reviewed = True
        self.is_rejected = True
        self.rejected_by = user
        self.reject_reason = reject_reason
        self.save()

    def view_by(self):
        self.is_reviewed = True
        self.save()

    def approve_by(self):
        self.is_reviewed = True
        self.is_approved = True
        self.save()

    class Meta:
        unique_together = ('veloce_app', 'reviewed_by')

    def __str__(self):
        return self.reviewed_by.username


class ApplicationStep1(models.Model):
    application = models.OneToOneField(VeloceApplication, on_delete=models.CASCADE)
    coborrower = models.ForeignKey(User, models.CASCADE, related_name="coborrower", blank=True, null=True)
    borrower_email = models.CharField(max_length=32, verbose_name="Borower Email <small class=asterisk>*</small>", blank=True, null=True)
    bill_no = models.CharField(max_length=20, verbose_name="Bill No <small class=asterisk>*</small>", blank=True, null=True)
    bill_amount = models.PositiveIntegerField(verbose_name="Total Bill Amount <small class=asterisk>*</small>", blank=True, null=True)
    bill_date = models.DateField(verbose_name="Bill Date <small class=asterisk>*</small>", blank=True, null=True)
    billing_party_name = models.CharField(max_length=50,
                                          verbose_name="Billing Party Name <small class=asterisk>*</small>", blank=True, null=True)
    inquired_by = models.CharField(max_length=50, verbose_name=" INQUIRED BY / Billing Party Email", blank=True,
                                   null=True)
    down_payment = models.DecimalField(decimal_places=2, max_digits=12,
                                       verbose_name="Down Payment <small class=asterisk>*</small>", default=0, blank=True, null=True)
    required_loan_amount = models.DecimalField(decimal_places=2, max_digits=12,
                                               verbose_name="Require Loan Amount <small class=asterisk>*</small>")
    loan_reason = models.SmallIntegerField(choices=enums.to_choices(enums.LoanReason),
                                           verbose_name="Reason", null=True, blank=True)
    emi_on_past_finance = models.IntegerField(default=0, verbose_name="EMI On Past Finance Availed")
    current_loan_emi = models.DecimalField(decimal_places=2, max_digits=12,
                                           verbose_name="Current Loan EMI <small class=asterisk>*</small>", default=0)
    total_emi = models.DecimalField(decimal_places=2, max_digits=12,
                                    verbose_name="Total EMI <small class=asterisk>*</small>", default=0)
    dealers_given_finance_scheme = models.CharField(max_length=20, null=True, blank=True, verbose_name="Finance Scheme")

    def __str__(self):
        return self.application.user.username


class InvoiceStep1(models.Model):
    application = models.OneToOneField(VeloceApplication, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, models.CASCADE)
    invoice_amount = models.IntegerField()
    downpayment_amount = models.IntegerField()
    tenure = models.CharField(max_length=2, verbose_name='Loan Tenure (Months)')
    invoice_proof = models.FileField(upload_to=UploadPath("invoice"), validators=[validators.FileValidator])

    def __str__(self):
        return self.application.user.username


class ApplicationStep2(models.Model):
    application = models.OneToOneField(
        VeloceApplication, on_delete=models.CASCADE
    )

    bank_account_number = models.CharField(
        max_length=25,
        validators=[validators.BankNumberValidator],
        verbose_name="Bank Account Number <small class=asterisk>*</small>"
    )
    ifsc_code = models.CharField(
        max_length=50,
        validators=[validators.IFSCValidator],
        verbose_name="IFSC code <small class=asterisk>*</small>"
    )
    bank_name = models.CharField(
        max_length=50,
        verbose_name="Bank Name <small class=asterisk>*</small>"
    )

    borrower_bank_account_number = models.CharField(
        max_length=25,
        verbose_name="Bank Account Number <small class=asterisk>*</small>",
        validators=[validators.BankNumberValidator]
    )
    borrower_ifsc_code = models.CharField(
        max_length=50,
        verbose_name="IFSC code <small class=asterisk>*</small>",
        validators=[validators.IFSCValidator]
    )
    borrower_bank_name = models.CharField(
        max_length=50,
        verbose_name="Bank Name <small class=asterisk>*</small>"
    )

    def __str__(self):
        return self.application.user.username


MODELS = {
    enums.ApplicationType.INVOICE.value: [
        InvoiceStep1,
        ApplicationStep2
    ],
    enums.ApplicationType.LOAN.value: [
        ApplicationStep1,
        ApplicationStep2
    ]
}


class GeneralVeloceMarkup(models.Model):
    MARKUP_PAYMENT_BY = (
        ("1", "Borrower"),
        ("2", "Lender"),
    )
    markup_percentage = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    markup_payment_by = models.CharField(choices=MARKUP_PAYMENT_BY, default="1", max_length=1)

    def __str__(self):
        return str(self.markup_percentage)


class DealerSpecialVeloceMarkup(models.Model):
    MARKUP_PAYMENT_BY = (
        ("1", "Borrower"),
        ("2", "Lender"),
    )
    markup_percentage = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    markup_payment_by = models.CharField(choices=MARKUP_PAYMENT_BY, default="1", max_length=1)
    dealer = models.OneToOneField(User, related_name="dealer", on_delete=models.CASCADE)

    def __str__(self):
        return self.dealer.username

class ApplicationSpecialVeloceMarkup(models.Model):
    MARKUP_PAYMENT_BY = (
        ("1", "Borrower"),
        ("2", "Lender"),
    )
    markup_percentage = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    markup_payment_by = models.CharField(choices=MARKUP_PAYMENT_BY, default="1", max_length=1)
    loan_application_no = models.OneToOneField(VeloceApplication, related_name="loan_application_no",
                                               on_delete=models.CASCADE)

    def __str__(self):
        return self.loan_application_no.user.username


class FinanceSchemeConfig(models.Model):
    interest_percentage = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)

    def __str__(self):
        return str(self.interest_percentage)


class ApplicationPaymentStatus(models.Model):
    application = models.OneToOneField(VeloceApplication, related_name='app_fee', on_delete=models.CASCADE, null=True,
                                       blank=True)
    payment_info = JSONField()
    payment_request_id = models.CharField(max_length=255, null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.application.user.username
