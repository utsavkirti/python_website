from django.http.response import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from veloce import forms, models, methods, enums, message
from django.template.response import TemplateResponse
from django.contrib import messages
from veloce.decorators import level_required

REQUIRED_LEVEL = 1


@login_required
@level_required(REQUIRED_LEVEL + 2)
def my_loans_app(request):
    success = ''
    error = ''
    if request.GET.get('success', '') == '1':
        success = message.STEP_SUCCESS_MSG
    if request.GET.get('error', '') == '1':
        error = message.STEP_ERROR_MSG
    if request.GET.get('error', '') == '2':
        app_id = request.GET.get('id')
        error = "Loan application No " + app_id + " has already submitted for this inquiry!!!"
    user = auth.get_user(request)
    applications = []
    veloce_app = models.VeloceApplication.objects.filter(user=user, is_approved=False, is_reviewed=False).order_by("-id")
    for app in veloce_app:
        applications += models.ReviewedVeloceApplication.objects.filter(veloce_app=app).distinct('veloce_app')
        
    return TemplateResponse(request, 'veloce/loans/my-loan-app-list.html', {
        'applications': applications,
        'success': success,
        'error': error,
        'sanctioned': True
    })


@login_required
@level_required(REQUIRED_LEVEL + 2)
def my_accepted_loans_app(request):
    success = ''
    error = ''
    if request.GET.get('success', '') == '1':
        success = message.STEP_SUCCESS_MSG
    if request.GET.get('error', '') == '1':
        error = message.STEP_ERROR_MSG
    if request.GET.get('error', '') == '2':
        app_id = request.GET.get('id')
        error = "Loan application No " + app_id + " has already submitted for this inquiry!!!"
    user = auth.get_user(request)
    applications = models.VeloceApplication.objects.filter(user=user, is_approved=True, is_reviewed=True).order_by("-id")
    return TemplateResponse(request, 'veloce/loans/my-loan-app-list.html', {
        'applications': applications,
        'success': success,
        'error': error,
        'sanctioned': False
    })


@login_required
@level_required(REQUIRED_LEVEL + 2)
def my_loans(request, app_id):
    success = ''
    if request.GET.get("success") == '1':
        success = message.VIEW_LOAN_SUCCESS_MSG

    invoices = models.Loan.objects.filter(
        application__application_type=enums.ApplicationType.INVOICE.value
    )
    my_deals = invoices.filter(application__user=request.user)
    my_purchases = invoices.filter(application__invoicestep1__customer=request.user)
    my_loans = models.Loan.objects.filter(
        application__application_type=enums.ApplicationType.LOAN.value,
        application__user=request.user,
        application_id=app_id
    )
    user_acc = models.Profile.objects.get(user=request.user)
    output = (my_deals | my_purchases | my_loans).all()
    for loan in output:
        loan.stats = loan.get_stats(request.user, user_acc.account_type)
        loan.coborrower = loan.my_coborrower(request.user)
        borrower = models.ApplicationStep1.objects.get(application_id=app_id)
        loan.borrower = borrower
    return TemplateResponse(
        request,
        "veloce/loans/list.html",
        {'loans': output, 'success': success, 'title': 'Sanctioned Loans'}
    )


@login_required
@level_required(REQUIRED_LEVEL + 1)
def my_approved_loans(request):
    success = ''
    if request.GET.get("success") == '1':
        success = message.VIEW_LOAN_SUCCESS_MSG

    invoices = models.Loan.objects.filter(
        application__application_type=enums.ApplicationType.INVOICE.value
    )
    my_deals = invoices.filter(application__user=request.user)
    my_purchases = invoices.filter(application__invoicestep1__customer=request.user)
    my_loans = models.Loan.objects.filter(
        is_coaccepted=False,
        application__application_type=enums.ApplicationType.LOAN.value,
        app_reviewed_by__reviewed_by=request.user,
        application__is_reviewed=True,
        application__is_approved=True
    )
    user_acc = models.Profile.objects.get(user=request.user)
    output = (my_deals | my_purchases | my_loans).all()
    for loan in output:
        loan.stats = loan.get_stats(request.user, user_acc.account_type)
        loan.coborrower = loan.my_coborrower(request.user)
        borrower = models.ApplicationStep1.objects.get(application=loan.application)
        loan.borrower = borrower

    return TemplateResponse(
        request,
        "veloce/loans/list.html",
        {'loans': output, 'success': success, 'title': 'Sanctioned Loans'}
    )


@login_required
@level_required(REQUIRED_LEVEL + 1)
def my_disbursement_loans(request):
    success = ''
    if request.GET.get("success") == '1':
        success = message.VIEW_LOAN_SUCCESS_MSG

    invoices = models.Loan.objects.filter(
        application__application_type=enums.ApplicationType.INVOICE.value
    )
    my_deals = invoices.filter(application__user=request.user)
    my_purchases = invoices.filter(application__invoicestep1__customer=request.user)
    my_loans = models.Loan.objects.filter(
        is_coaccepted=True,
        application__application_type=enums.ApplicationType.LOAN.value,
        app_reviewed_by__reviewed_by=request.user,
        application__is_reviewed=True,
        application__is_approved=True
    )
    user_acc = models.Profile.objects.get(user=request.user)
    output = (my_deals | my_purchases | my_loans).all()
    for loan in output:
        loan.stats = loan.get_stats(request.user, user_acc.account_type)
        loan.coborrower = loan.my_coborrower(request.user)
        borrower = models.ApplicationStep1.objects.get(application_id=loan.application.id)
        loan.borrower = borrower

    return TemplateResponse(
        request,
        "veloce/loans/list.html",
        {'loans': output, 'success': success, 'title': 'Sanctioned Loans'}
    )



@login_required
@level_required(REQUIRED_LEVEL + 2)
def loans(request):
    output = []
    loans = models.Loan.objects.filter(is_accepted=True)
    user_acc = models.Profile.objects.get(user=request.user)
    for loan in loans:
        if not loan.has_coborrower_accepted:
            continue
        output.append(loan)
        loan.stats = loan.get_stats(request.user, user_acc.account_type)
    return TemplateResponse(
        request,
        "veloce/loans/list.html",
        {'loans': output, 'lender': True}
    )


@login_required
@level_required(REQUIRED_LEVEL + 2)
def view_loan(request, loan_id):
    current_loan_emi = 0
    loan = models.Loan.objects.get(pk=loan_id)
    application_details = models.ApplicationStep1.objects.get(application=loan.application.id)
    fiance_details = None
    lender = None
    lender_details = models.ReviewedVeloceApplication.objects.filter(id=loan.app_reviewed_by.id)
    lender = models.Profile.objects.get(user=lender_details[0].reviewed_by)
    
    get_bill_info = models.VeloceBooksale.objects.using('marketplace').get(inquiry_id=loan.application.inquiry_id)
    if get_bill_info.dealers_given_finance_scheme:
        fiance_details = get_bill_info
    else:
        current_loan_emi = methods.application.emi_calculator(loan.interest_rate, loan.sanctioned_loan_amount, loan.loan_tenure)
    borrower = loan.application.user == request.user or loan.application.coborrower == request.user

    if request.method == 'POST':
        if loan.application.user == request.user:
            loan.is_accepted = True
            loan.save()
            models.VeloceApplication.objects.filter(id=loan.application.id).update(is_approved=True, is_reviewed=True)
            models.Loan.objects.filter(application=loan.application, is_accepted=False).delete()
            models.ReviewedVeloceApplication.objects.filter(~Q(reviewed_by=loan.app_reviewed_by.reviewed_by),
                                                            veloce_app=loan.application).update(is_approved=False,
                                                                                                is_reviewed=True,
                                                                                                is_rejected=True,
                                                                                               # rejected_by=request.user,
                                                                                                reject_reason="Loan has been approved for other lender!")
            return redirect("my-loans", loan.application.id)
        elif loan.application.coborrower == request.user:
            loan.is_coaccepted = True
            loan.save()
            return redirect("my-loans", loan.application.id)

    return TemplateResponse(request, "veloce/loans/view.html", {
        'loan': loan,
        'application_details': application_details,
        'fiance_details': fiance_details,
        'funded_pct': loan.funded_pct(),
        'lender': not borrower,
        'current_emi': current_loan_emi,
        'lender_details': lender
    })


@login_required
@level_required(REQUIRED_LEVEL + 2)
def fund_loan(request, loan_id):
    error = ''
    loan = models.Loan.objects.get(pk=loan_id)
    loan_amount = loan.loan_amount
    if request.method == 'POST':
        form = forms.FundForm(request.POST, label_suffix='')
        if form.is_valid():
            user = request.user
            funds = models.Lender(
                user=user,
                loan=loan,
                loan_amount=request.POST['amount']
            )
            funds.save()
            return redirect('overview')
        else:
            error = 'Loan funding unsuccessful. Please correct the errors below.'
    else:
        form = forms.FundForm(label_suffix='')

    return TemplateResponse(request, "veloce/loans/fund.html", {
        'form': form,
        'amount': loan_amount,
        'error': error
    })


@login_required
@level_required(REQUIRED_LEVEL + 2)
def disburse_loan(request, loan_id):
    loan = models.Loan.objects.get(pk=loan_id)
    veloce_app = models.VeloceApplication.objects.get(id=loan.application.id)
    if loan.is_coaccepted:
        messages.info(request, 'Loan with id {0} is already offered!'.format(loan.id))
    else:
        messages.success(request, 'Loan for Application No {0} has been Disbursed successfully!'.format(veloce_app.id))
        loan.is_coaccepted = True
        loan.save()
    return redirect('my_disbursement_loans')


# ravi
@login_required
def user_dashboard(request):
    # context ={
    #     'user_own_loan' : 'user_own_loan',
    # }
    # return HttpResponse('<h1>This is the dashboard page</h1>')
    # return render(request,'veloce/loans/load-dashboard.html',context)
    user_own_loans = models.Loan.objects.filter(application__user = request.user)
    if request.user.is_authenticated:
        if request.user.profile.account_type == 3:
            return redirect('admin-borrower-applications')
        else:
            return TemplateResponse(request, "veloce/loans/load-dashboard.html", {'user_own_loans' : user_own_loans})
    else:
        return TemplateResponse(request, "veloce/loans/load-dashboard.html", {'user_own_loans' : user_own_loans})
