from django.db import models
from django.contrib.auth.models import User
from veloce import validators
from veloce import enums
from veloce.models import VeloceApplication, ReviewedVeloceApplication
from django.utils.deconstruct import deconstructible
import uuid
from django.core.validators import MinValueValidator


class Loan(models.Model):
    application = models.ForeignKey(VeloceApplication, models.CASCADE)
    app_reviewed_by = models.ForeignKey(ReviewedVeloceApplication, related_name='app_reviewed_by',
                                        on_delete=models.CASCADE, null=True, blank=True)
    loan_amount = models.PositiveIntegerField(
        verbose_name="Requested Loan Amount")  # ,Remove Decimal and Max 7 digit only added by Piyush
    sanctioned_loan_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    disbursement_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    dealer_scheme_roi = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True)
    dealer_scheme_emi = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True,
                                            verbose_name='Dealer Scheme EMI')
    loan_tenure = models.SmallIntegerField(verbose_name='Loan Tenure (Months)', validators=[MinValueValidator(1)])  # ,max_length=3  added by Piyush
    interest_rate = models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Annual Interest Rate (%)')
    lender_amount_after_veloce_roi = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True, verbose_name="Lender Amount After Veloce Markup")
    lender_roi_after_veloce_roi = models.DecimalField(decimal_places=4, max_digits=8, null=True, blank=True)
    veloce_amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    veloce_roi = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    is_coaccepted = models.BooleanField(default=False)
    created_at = models.DateField(auto_now=True)
    accepted_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.application.user.username

    @staticmethod
    def inverse_emi(n, r, emi):
        f = (1 + r) ** n
        return round(emi * (f - 1) / (r * f), 2)

    @property
    def has_coborrower_accepted(self):
        return self.application.coborrower is None or self.is_coaccepted

    def emi_per(self, principal):
        r = self.interest_rate / 1200
        f = self.loan_tenure
        import numpy
        return round(numpy.pmt(r, f, -principal, 0, 0), 2)

    def emi(self):
        if not self.dealer_scheme_emi > 0:
            return self.emi_per(self.loan_amount)
        else:
            return self.dealer_scheme_emi

    def funded(self):
        return sum([lender.loan_amount for lender in self.lender_set.all()])

    def funded_pct(self):
        return round(self.funded() * 100 / self.loan_amount, 1)

    def get_stats(self, user, user_acc):
        if self.application.user == user:
            print("working", user_acc)
            disbursement_amount = self.lender_amount_after_veloce_roi
        elif not self.dealer_scheme_emi > 0 and user_acc != 2:
            print("elif", user_acc)
            disbursement_amount = self.disbursement_amount
        else:
            print('else')
            disbursement_amount = self.lender_amount_after_veloce_roi
        if not self.dealer_scheme_emi > 0:
            interest_rate = self.interest_rate
        else:
            interest_rate = self.lender_roi_after_veloce_roi
        coborrower = self.application.coborrower
        title = self.application.coborrower_title
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", disbursement_amount)
        if coborrower != user and user_acc == 3:
            return {
                'Loan Amount': f"₹{self.loan_amount:0.2f}",
                'Interest Rate': f"{interest_rate}% p.a.",
                'Disbursement Amount': f"₹{disbursement_amount:0.2f}",
            }
        else:
            return {
                'Loan Amount': f"₹{self.loan_amount:0.2f}",
                'Interest Rate': f"{self.lender_roi_after_veloce_roi}% p.a.",
                'Disbursement Amount': f"₹{disbursement_amount:0.2f}",
            }

    def my_coborrower(self, user):
        coborrower = self.application.coborrower
        if coborrower == user:
            return self.application.user
        else:
            return coborrower

    class Meta:
        unique_together = ('application', 'app_reviewed_by',)


class Lender(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    loan = models.ForeignKey(Loan, models.CASCADE)
    loan_amount = models.DecimalField(decimal_places=0,
                                      max_digits=7)  # ,Remove Decimal and Max 7 digit only added by Piyush
    def __str__(self):
        return self.user.username

    def emi(self):
        n = self.loan.loan_tenure
        r = self.loan.interest_rate / (n * 100)
        f = (1 + r) ** n
        emi = (self.loan_amount * r * f) / (f - 1)
        return round(emi, 2)
