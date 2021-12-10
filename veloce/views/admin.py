from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import redirect, reverse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from veloce import forms
from veloce import models
from veloce import enums
from veloce.module_map import MODULE_MAP
from django.conf import settings
from veloce.decorators import level_required
import json, requests
import numpy
REQUIRED_LEVEL = 2


@login_required
@level_required(REQUIRED_LEVEL + 1)
def borrower_applications(request):
    success = ''
    error = ''
    is_approved_status = False
    if request.GET.get('success') == '1':
        success = 'Application sanctioned successfully!'
    elif request.GET.get('error') == '1':
        error = 'Application rejected successfully!'

    sort_by = int(request.GET.get('sortBy', 0))
    filter_by = int(request.GET.get('filterBy', 0))
    is_reviewed = filter_by != 0
    is_approved = filter_by == 2
    ascending = (sort_by % 2) == 0
    if sort_by in [2, 3]:
        def key(x):
            try:
                return x.applicationstep1.required_loan_amount
            except Exception as e:
                return x.veloce_app.applicationstep1.required_loan_amount
            except Exception as l:
                return x.application.applicationstep1.required_loan_amount
    else:
        def key(x):
            return x.created_at

    applications = []
    is_loan_app = ''
    is_rejected_app = ''
    if filter_by == 1:
        is_approved_status = True
        for a in models.application.MODELS:
            applications += models.ReviewedVeloceApplication.objects.filter(
                is_approved=False,
                is_rejected=True,
                is_reviewed=is_reviewed,
                veloce_app__current_step=len(models.application.MODELS[a]) + 1,
                veloce_app__application_type=a,
                reviewed_by=request.user
            ).all()
        is_rejected_app = True
    elif filter_by == 2:
        is_approved_status = True
        for a in models.application.MODELS:
            applications += models.ReviewedVeloceApplication.objects.filter(
                ~Q(veloce_app__is_approved=is_approved),
                ~Q(veloce_app__is_reviewed=is_reviewed),
                is_approved=is_approved,
                is_reviewed=is_reviewed,
                veloce_app__current_step=len(models.application.MODELS[a]) + 1,
                veloce_app__application_type=a,
                reviewed_by=request.user
            ).all()
    elif filter_by == 3:
        is_approved_status = False
        is_loan_app = 'Accepted'
        for all_app in models.VeloceApplication.objects.all():            
            for reviewapp in models.ReviewedVeloceApplication.objects.filter(is_approved=True, is_reviewed=True, veloce_app=all_app, reviewed_by=request.user):
                applications += models.Loan.objects.filter(
                    is_accepted=True,
                    is_coaccepted=False,
                    application=all_app,
                    app_reviewed_by=reviewapp,
                ).all()
    elif filter_by == 4:
        is_approved_status = False
        is_loan_app = 'Disbursed'
        for all_app in models.VeloceApplication.objects.all():            
            for reviewapp in models.ReviewedVeloceApplication.objects.filter(is_approved=True, is_reviewed=True, veloce_app=all_app, reviewed_by=request.user):
                applications += models.Loan.objects.filter(
                    is_accepted=True,
                    application=all_app,
                    app_reviewed_by=reviewapp,
                    is_coaccepted=True
                ).all()
    else:
        is_approved_status = False
        for all_app in models.VeloceApplication.objects.all():
            if not models.ReviewedVeloceApplication.objects.filter(Q(is_reviewed=True, is_approved=True) | Q(is_rejected=True), reviewed_by=request.user, veloce_app_id=all_app.id).exists():
                for a in models.application.MODELS:
                    applications += models.VeloceApplication.objects.filter(
                        id=all_app.id,
                        current_step=len(models.application.MODELS[a]) + 1,
                        application_type=a
                    ).all()
    applications = sorted(applications, key=key, reverse=not ascending)
    return TemplateResponse(request, 'veloce/admin/applications.html', {
        'applications': applications,
        'success': success,
        'error': error,
        'filter_by': filter_by if "filterBy" in request.GET else None,
        'sort_by': sort_by,
        'is_approved_status': is_approved_status,
        'is_loan_app': is_loan_app,
        'is_rejected_app': is_rejected_app
    })


@login_required
@level_required(REQUIRED_LEVEL + 1)
def review_application(request, app_id):
    app = models.VeloceApplication.objects.get(pk=app_id)
    is_approved_by_lender = False
    review_app = models.ReviewedVeloceApplication.objects.filter(veloce_app=app, reviewed_by=request.user)
    if review_app.exists():
        if review_app[0].is_approved or review_app[0].is_rejected:
            is_approved_by_lender = True

    # Finance calculations
    # import numpy
    import numpy_financial as npf
    get_inq_id = models.VeloceApplication.objects.get(id=app_id)
    get_required_loan_amt = models.ApplicationStep1.objects.get(application=get_inq_id)
    try:
        get_bill_info = models.VeloceBooksale.objects.using('marketplace').get(inquiry_id=get_inq_id.inquiry_id)
    except:
        get_bill_info = ""


    check_finance_available = 'false'

    if get_bill_info:
        if get_bill_info.dealers_given_finance_scheme:
            interest_val = (get_bill_info.dealers_given_finance_scheme.rate_of_interest / 12) / 100
            required_amt = int(get_required_loan_amt.required_loan_amount)
            # emi = numpy.pmt(interest_val, get_bill_info.dealers_given_finance_scheme.tenure, -required_amt, 0, 0)
            emi = npf.pmt(interest_val, get_bill_info.dealers_given_finance_scheme.tenure, -required_amt, 0, 0)
            total_emi = emi * get_bill_info.dealers_given_finance_scheme.tenure
            total_interest = total_emi - required_amt
            rate_of_interest = get_bill_info.dealers_given_finance_scheme.rate_of_interest
            tenure = get_bill_info.dealers_given_finance_scheme.tenure
            check_finance_available = 'true'
        else:
            required_amt = 0
            rate_of_interest = 0
            tenure = 0
            emi = 0
            total_emi = 0
            total_interest = 0
    else:
        required_amt = 0
        rate_of_interest = 0
        tenure = 0
        emi = 0
        total_emi = 0
        total_interest = 0

    # Finance calc done
    modules = MODULE_MAP[app.application_type]
    if request.method == 'POST':
        return redirect(reverse('admin-borrower-applications') + "?success=1")

    show_forms = forms.utils.display_forms(app, modules)

    borrower1 = {
        'name': app.user.first_name + " " + app.user.last_name,
        'email': app.user.email,
        'id': app.user.id,
        'co_borrower_email': get_required_loan_amt.borrower_email,
        'type': enums.human_readable(enums.AccountType(app.user.profile.account_type).name),
        'title': app.user_title,
        'url': "/display-user-details-to-lender/?email=" + str(get_required_loan_amt.borrower_email) + "&type=Borrower",
        'verified': app.user.profile.is_verified
    }
    print("^^^^^^^^^^^66", borrower1, enums.human_readable(enums.AccountType(app.user.profile.account_type).name), app.user)
    borrower2 = None
    coborrower = app.coborrower
    if coborrower:
        borrower2 = {
            'name': coborrower.first_name + " " + coborrower.last_name,
            'email': coborrower.email,
            'type': enums.human_readable(enums.AccountType(coborrower.profile.account_type).name),
            'title': app.coborrower_title,
            'url': "/display-user-details-to-lender/?email=" + str(get_required_loan_amt.coborrower.email) + "&type=Coborrower",
            'verified': coborrower.profile.is_verified
        }

    return TemplateResponse(request, 'veloce/admin/application.html', {
        'forms': show_forms,
        'application': app,
        'borrower1': borrower1,
        'borrower2': borrower2,
        'required_amt': required_amt,
        'rate_of_interest': rate_of_interest,
        'tenure': tenure,
        'emi': round(emi, 2),
        'total_emi': round(total_emi, 2),
        'total_interest': round(total_interest, 2),
        'check_finance_available': check_finance_available,
        'is_approved_by_lender': is_approved_by_lender
    })


@login_required
@level_required(REQUIRED_LEVEL + 1)
def approve_application(request, app_id):
    app = models.VeloceApplication.objects.get(pk=app_id)
    app_is_approved = app.is_approved
    is_loan_instance = False
    modules = MODULE_MAP[app.application_type]
    check_reviewed_app = models.ReviewedVeloceApplication.objects.filter(veloce_app=app, reviewed_by=request.user)
    if check_reviewed_app.count() > 0:
        reviewed_app = models.ReviewedVeloceApplication.objects.get(veloce_app=app, reviewed_by=request.user)
        reviewed_app.view_by()
    else:
        reviewed_app = models.ReviewedVeloceApplication.objects.create(veloce_app=app, reviewed_by=request.user)
        reviewed_app.view_by()
    review_app = models.ReviewedVeloceApplication.objects.get(veloce_app=app, reviewed_by=request.user)
    is_approved_by_lender = False
    if review_app.is_approved or review_app.is_rejected:
        is_approved_by_lender = True
    context = {}
    interest_rate = 12
    if app.application_type == enums.ApplicationType.INVOICE.value:
        invoice_details = app.invoicestep1
        tenure = invoice_details.tenure
        repay_amount = float(invoice_details.invoice_amount - invoice_details.downpayment_amount)
        loan_amount = float(models.Loan.inverse_emi(tenure, interest_rate / 1200, repay_amount / tenure))
        loan = models.Loan(
            interest_rate=interest_rate,
            loan_amount=loan_amount,
            loan_tenure=tenure,
            application=app
        )
        context['repay'] = repay_amount
    else:
        is_finance_available = 'false'
        check_approved = check_reviewed_app.filter(is_approved=True, is_reviewed=True)
        if check_approved.count() > 0:
            loan = models.Loan.objects.get(application=app, app_reviewed_by=check_approved[0])
            if loan:
                is_loan_instance = True
        else:
            if review_app.is_approved:
                loan_data = models.Loan.objects.get(application=app, app_reviewed_by=request.user)
                sanctioned_loan_amount = loan_data.loan_amount
                tenure = loan_data.loan_tenure
                dealer_scheme_roi = loan_data.loan_tenure
                dealer_scheme_emi = loan_data.dealer_scheme_roi
                disbursement_amount = loan_data.disbursement_amount
            elif review_app.is_rejected:
                sanctioned_loan_amount = app.applicationstep1.required_loan_amount
                tenure = 0
                dealer_scheme_roi = 0
                dealer_scheme_emi = 0
                disbursement_amount = app.applicationstep1.required_loan_amount
            else:
                # import numpy
                import numpy_financial as npf
                try:
                    get_bill_info = models.VeloceBooksale.objects.using('marketplace').get(inquiry_id=app.inquiry_id)
                except:
                    get_bill_info = ""

                # print('-------------> ',get_bill_info)    
                if get_bill_info:
                    if get_bill_info.dealers_given_finance_scheme:
                        d_loan_amt = int(app.applicationstep1.required_loan_amount)
                        d_roi = int(get_bill_info.dealers_given_finance_scheme.rate_of_interest)
                        d_tenure = int(get_bill_info.dealers_given_finance_scheme.tenure)
                        d_interest_rate = (d_roi / 12) / 100
                        total_emi = round(numpy.pmt(d_interest_rate, d_tenure, -d_loan_amt, 0, 0), 2)
                        total_emi = round(npf.pmt(d_interest_rate, d_tenure, -d_loan_amt, 0, 0), 2)
                        sanctioned_loan_amount = app.applicationstep1.required_loan_amount
                        dealer_scheme_emi = total_emi
                        int_rate = (interest_rate / 12) / 100
                        # disbursement_amount = numpy.pv(int_rate, d_tenure, -total_emi, 0, 0)
                        disbursement_amount = npf.pv(int_rate, d_tenure, -total_emi, 0, 0)
                        dealer_scheme_roi = d_roi
                        tenure = d_tenure
                        is_finance_available = 'true'
                    else:
                        # sanctioned_loan_amount = app.applicationstep1.required_loan_amount
                        # tenure = 0
                        # dealer_scheme_roi = 0
                        # dealer_scheme_emi = 0
                        # disbursement_amount = sanctioned_loan_amount #app.applicationstep1.required_loan_amount

                        # sanctioned_loan_amount = int(request.POST.get('sanctioned_loan_amount',False))
                        # tenure = int(request.POST.get('tenure',False))
                        # dealer_scheme_roi = 0
                        # dealer_scheme_emi = 0
                        # interest_rate = (int(request.POST.get('tenure',False)) / 12) / 100
                        # print('CHERIL GANDHI ',interest_rate)
                        # disbursement_amount=float(sanctioned_loan_amount) * float(interest_rate)
                        # # * float(pow(1+float(interest_rate),tenure))/float((pow(1+float(interest_rate),tenure)-1))
                        
                        sanctioned_loan_amount = app.applicationstep1.required_loan_amount
                        tenure = 24
                        dealer_scheme_roi = 0
                        dealer_scheme_emi = 0
                        interest_rate = (10 / 12) / 100
                        disbursement_amount=float(sanctioned_loan_amount) * float(interest_rate) * pow(1+float(interest_rate),tenure)/(pow(1+float(interest_rate),tenure)-1)
                else:
                    sanctioned_loan_amount = app.applicationstep1.required_loan_amount
                    tenure = 0
                    dealer_scheme_roi = 0
                    dealer_scheme_emi = 0
                    # disbursement_amount=float(sanctioned_loan_amount) * float(interest_rate) * pow(1+float(interest_rate),tenure)/(pow(1+float(interest_rate),tenure)-1)
                    disbursement_amount = sanctioned_loan_amount #app.applicationstep1.required_loan_amount
            loan = models.Loan(
                loan_amount=app.applicationstep1.required_loan_amount,
                dealer_scheme_roi=dealer_scheme_roi,
                dealer_scheme_emi=round(dealer_scheme_emi, 2),
                sanctioned_loan_amount=sanctioned_loan_amount,
                interest_rate=interest_rate,
                loan_tenure=tenure,
                disbursement_amount=round(disbursement_amount, 2),
                application=app
            )
            
    if request.method == 'POST':
        form = forms.ApplicationApproveForm(request.POST, instance=loan, label_suffix='')
        if form.is_valid():
            veloce_marku_rate = 2
            check_app_spl_v_markup = models.ApplicationSpecialVeloceMarkup.objects.filter(loan_application_no=app_id)
            check_dealer_spl_v_markup = models.DealerSpecialVeloceMarkup.objects.filter(dealer=app.user)
            check_general_spl_v_markup = models.GeneralVeloceMarkup.objects.all()
            if check_app_spl_v_markup.exists():
                veloce_marku_rate = int(round(check_app_spl_v_markup[0].markup_percentage))
            elif check_dealer_spl_v_markup.exists():
                veloce_marku_rate = int(round(check_dealer_spl_v_markup[0].markup_percentage))
            elif check_general_spl_v_markup.exists():
                veloce_marku_rate = int(round(check_general_spl_v_markup[0].markup_percentage))
            check_reviewed_app = models.ReviewedVeloceApplication.objects.filter(veloce_app=app, reviewed_by=request.user)
            if check_reviewed_app.count() > 0:
                reviewed_app = models.ReviewedVeloceApplication.objects.get(veloce_app=app, reviewed_by=request.user)
                reviewed_app.approve_by()
            else:
                reviewed_app = models.ReviewedVeloceApplication.objects.create(veloce_app=app, reviewed_by=request.user)
                reviewed_app.approve_by()
            loan_form = form.save(commit=False)
            loan_form.app_reviewed_by = reviewed_app

            # velcoe amount calculations start
            lender_amount_after_veloce_roi = 0
            lender_roi_after_veloce_roi = 0
            veloce_amount = 0
            # import numpy
            import numpy_financial as npf
            try:
                get_bill_info = models.VeloceBooksale.objects.using('marketplace').get(inquiry_id=app.inquiry_id)
            except:
                get_bill_info = ""

            if get_bill_info.dealers_given_finance_scheme:
                d_loan_amt = int(app.applicationstep1.required_loan_amount)
                d_roi = int(get_bill_info.dealers_given_finance_scheme.rate_of_interest)
                d_tenure = int(get_bill_info.dealers_given_finance_scheme.tenure)
                d_interest_rate = (d_roi / 12) / 100
                # total_emi = round(numpy.pmt(d_interest_rate, d_tenure, -d_loan_amt, 0, 0), 2)
                total_emi = round(npf.pmt(d_interest_rate, d_tenure, -d_loan_amt, 0, 0), 2)
                get_disbursement_amount = float(request.POST['disbursement_amount'])
                veloce_amount = round((get_disbursement_amount * (veloce_marku_rate / 100)), 2)
                lender_amount_after_veloce_roi = (get_disbursement_amount - veloce_amount)
                try:
                    # lender_roi_after_veloce_roi_calc = numpy.rate(d_tenure, -total_emi, lender_amount_after_veloce_roi, 0,0)
                    lender_roi_after_veloce_roi_calc = npf.rate(d_tenure, -total_emi, lender_amount_after_veloce_roi, 0,0)
                    lender_roi_after_veloce_roi = round(((lender_roi_after_veloce_roi_calc * 12) * 100), 4)
                except Exception as e:
                    print(e)
            else:
                print("else working")
                d_loan_amt = int(app.applicationstep1.required_loan_amount)
                interest_rate = (float(request.POST['interest_rate']) / 12) / 100
                total_emi = round(numpy.pmt(interest_rate, int(request.POST['loan_tenure']), -int(float(request.POST['disbursement_amount'])), 0, 0), 2)
                total_emi = round(npf.pmt(interest_rate, int(request.POST['loan_tenure']), -int(float(request.POST['disbursement_amount'])), 0, 0), 2)
                get_disbursement_amount = float(request.POST['disbursement_amount'])
                veloce_amount = round((get_disbursement_amount * (veloce_marku_rate / 100)), 2)
                lender_amount_after_veloce_roi = (get_disbursement_amount - veloce_amount)
                try:
                    # lender_roi_after_veloce_roi_calc = numpy.rate(int(request.POST['loan_tenure']), -total_emi, lender_amount_after_veloce_roi, 0,0)
                    lender_roi_after_veloce_roi_calc = npf.rate(int(request.POST['loan_tenure']), -total_emi, lender_amount_after_veloce_roi, 0,0)
                    lender_roi_after_veloce_roi = round(((lender_roi_after_veloce_roi_calc * 12) * 100), 4)
                except Exception as e:
                    print(e)
            #velcoe amount calculations end

            loan_form.veloce_roi = veloce_marku_rate
            loan_form.veloce_amount = veloce_amount
            loan_form.lender_amount_after_veloce_roi = lender_amount_after_veloce_roi
            loan_form.lender_roi_after_veloce_roi = lender_roi_after_veloce_roi
            loan_form.save()
            return redirect(reverse('admin-borrower-applications') + "?success=1")
    else:
        form = forms.ApplicationApproveForm(instance=loan, label_suffix='')
    context['form'] = form
    context['id'] = app.id
    context['app_is_approved'] = app_is_approved
    context['is_submitted'] = is_approved_by_lender
    context['is_finance_available'] = is_finance_available
    context['is_loan_instance'] = is_loan_instance

    return TemplateResponse(request, 'veloce/admin/approve-application.html', context)


@login_required
@level_required(REQUIRED_LEVEL + 1)
def reject_application(request, app_id):
    app = models.VeloceApplication.objects.get(pk=app_id)
    check_reviewed_app = models.ReviewedVeloceApplication.objects.filter(veloce_app=app, reviewed_by=request.user)
    if check_reviewed_app.count() > 0:
        reviewed_app = models.ReviewedVeloceApplication.objects.get(veloce_app=app, reviewed_by=request.user)
        reviewed_app.view_by()
    else:
        reviewed_app = models.ReviewedVeloceApplication.objects.create(veloce_app=app, reviewed_by=request.user)
        reviewed_app.view_by()
    reviewed_app = models.ReviewedVeloceApplication.objects.get(veloce_app=app, reviewed_by=request.user)
    form = forms.ApplicationRejectForm(instance=reviewed_app, label_suffix='')
    if request.method == 'POST':
        form = forms.ApplicationRejectForm(request.POST, instance=app, label_suffix='')
        if form.is_valid():
            reviewed_app.reject(form.instance.reject_reason, request.user)
            return redirect(reverse('admin-borrower-applications') + "?error=1")
    return TemplateResponse(request, 'veloce/admin/reject-application.html', {'form': form, 'id': app.id})


@login_required
@level_required(REQUIRED_LEVEL + 1)
def calculate_disbursement_amount(request):
    # import numpy
    import numpy_financial as npf
    app_id = request.GET['app_id']
    roi = int(request.GET['roi'])
    print(app_id,roi)
    get_inq_id = models.VeloceApplication.objects.get(id=app_id)
    get_bill_info = models.VeloceBooksale.objects.using('marketplace').get(inquiry_id=get_inq_id.inquiry_id)
    if get_bill_info.dealers_given_finance_scheme:
        d_loan_amt = int(get_inq_id.applicationstep1.required_loan_amount)
        d_roi = int(get_bill_info.dealers_given_finance_scheme.rate_of_interest)
        d_tenure = int(get_bill_info.dealers_given_finance_scheme.tenure)
        interest_rate = (d_roi / 12) / 100
        # total_emi = round(numpy.pmt(interest_rate, d_tenure, -d_loan_amt, 0, 0), 2)
        total_emi = round(npf.pmt(interest_rate, d_tenure, -d_loan_amt, 0, 0), 2)
        interest_val = (roi / 12) / 100
        # disbursement_amount = numpy.pv(interest_val, d_tenure, -total_emi, 0, 0)
        disbursement_amount = npf.pv(interest_val, d_tenure, -total_emi, 0, 0)
        context = {
            "status": True,
            'disbursement_amount': round(disbursement_amount, 2)
        }
    else:
        context = {
            "status": False
        }
    return JsonResponse(context)

@login_required()
def display_user_details_to_lender(request):
    email = request.GET['email']
    type = request.GET['type']
    data = {
        'email': email
    }
    res = requests.get(settings.OAUTH_URL + '/user-details-by-id/', params=data).text
    response = json.loads(res)
    general = json.loads(response['data']['general'])
    address = json.loads(response['data']['address'])
    identification = ''
    company = ''
    additional_company = ''
    if response['data']['acc_type'] == 1:
        identification = json.loads(response['data']['identification'])
    else:
        company = json.loads(response['data']['company'])
        additional_company = json.loads(response['data']['add_company_details'])
    return TemplateResponse(request, 'veloce/admin/user-details-to-lender.html', {'data': response, 'general': general, 'address': address, 'identification': identification, 'company': company, 'additional_company': additional_company, 'email': email, 'type': type })