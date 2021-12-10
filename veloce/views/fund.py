from django.template.response import TemplateResponse
from veloce.decorators import profile_required
from veloce import forms
from veloce import models
from veloce import methods
from django.shortcuts import redirect
from veloce.decorators import allowed_user
from veloce import message

def save_fund(request, loan_id):
    loan = models.Loan.objects.get(pk=loan_id)
    loan_amount = loan.loan_amount
    if request.method == 'POST':
        form = forms.FundForm(request.POST, label_suffix='')
        if form.is_valid():
            user = request.user.veloceuser
            funds = models.Lender(
                veloce_user=user,
                loan=loan,
                loan_amount=request.POST['amount']
            )
            funds.save()
            return redirect('overview')
        else:
            error = message.SAVE_FUND_SUCCESS_MSG
    else:
        form = forms.FundForm(label_suffix='')
    return TemplateResponse(request, "veloce/fund.html", {'form': form, 'amount': loan_amount})