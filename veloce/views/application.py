from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from veloce import forms, models, methods, enums, message
from datetime import datetime
from django.conf import settings
from veloce.module_map import MODULE_MAP
from veloce.decorators import level_required
from django.http import JsonResponse
import requests

REQUIRED_LEVEL = 2


@login_required
@level_required(REQUIRED_LEVEL)
def new(request, application_type):
    user = auth.get_user(request)
    application_type = enums.ApplicationType.LOAN.value
    app = models.VeloceApplication(
        user=user,
        application_type=application_type
    )
    app.save()
    return redirect('step-application', app.pk, 1)


@login_required
@level_required(REQUIRED_LEVEL + 1)
def step(request, app_id, step=1):
    user = auth.get_user(request)
    print('user  ---- ',user)
    try:
        application = models.VeloceApplication.objects.get(pk=app_id, user=user)
    except ObjectDoesNotExist:
        return redirect('list-application')
    modules = MODULE_MAP[application.application_type]
    model, form = modules[step - 1]
    instance = None
    response = ''
    if step < 1:
        return redirect('list-application')
    elif application.current_step > len(modules):
        return redirect('/application/list?error=1')
    elif step > application.current_step:
        return redirect('step-application', app_id, application.current_step)
    elif step < application.current_step:
        instance = model.objects.filter(application__pk=application.pk)[0]
    check_payment = models.ApplicationPaymentStatus.objects.filter(application_id=app_id, payment_id__isnull=True)
    if request.method == 'POST':
        form_instance = form(
            request.POST,
            request.FILES,
            instance=instance,
            label_suffix=''
        )
        borrower = None
        if "borrower" in request.POST and request.POST['borrower']:
            borrower = request.POST['borrower'].split('-')[1]
        if form_instance.is_valid():
            if step + 1 > len(modules):
                try:
                    if check_payment.count() <= 0:
                        try:
                            response = methods.application.payment_api(request, app_id, step)
                            if response['success']:
                                models.ApplicationPaymentStatus.objects.create(application_id=app_id, payment_info=response['payment_request'])
                                methods.application.save_application_step(form_instance, application, borrower, step)
                                models.VeloceApplication.objects.filter(id=app_id).update(current_step=2)
                                app = models.VeloceApplication.objects.get(id=app_id)
                                is_financed = models.VeloceProductinquiry.objects.using('marketplace').filter(id=app.inquiry_id).update(is_product_financed=True)
                                return redirect(response['payment_request']['longurl'])
                            else:
                                return redirect('/application/list?error=' + str(response['message']))
                        except Exception as e:
                            print(e)
                            return redirect('/application/list?error=' + str(e))
                    elif check_payment.count() >= 0:
                        try:
                            response = methods.application.payment_api(request, app_id, step)
                            if response['success']:
                                payment = models.ApplicationPaymentStatus.objects.get(application_id=app_id)
                                payment.payment_info = response['payment_request']
                                payment.save()
                                app = models.VeloceApplication.objects.get(id=app_id)
                                is_financed = models.VeloceProductinquiry.objects.using('marketplace').get(id=app.inquiry_id)
                                is_financed.is_product_financed = 1
                                is_financed.save()
                                return redirect(response['payment_request']['longurl'])
                            else:
                                return redirect('/application/list?error=' + str(response['message']))
                        except Exception as e:
                            return redirect('/application/list?error=' + str(e))
                    else:
                        return redirect('/application/list?error=1')
                except Exception as e:
                    print("*********************************************")
                    print(e)
                    print("*********************************************")
                    return redirect(f'/application/{app_id}/step{step + 1}')
            else:
                methods.application.save_application_step(form_instance, application, borrower, step)
            return redirect(f'/application/{app_id}/step{step + 1}')
    else:
        if "payment_id" in request.GET:
            if check_payment[0].payment_id:
                return redirect('/application/list?error=1')
            else:
                check_payment.update(payment_id=request.GET['payment_id'], payment_request_id=request.GET['payment_request_id'])
                models.VeloceApplication.objects.filter(id=app_id).update(current_step=3)
                return redirect('/application/list?success=1')
        form_instance = form(instance=instance, label_suffix='')

    return TemplateResponse(request, 'veloce/application/step.html', {
        'form': form_instance, 'step': step, 'app_id': app_id,
        'prev': step - 1, 'num_steps': len(modules), 'fintech_url': settings.OAUTH_URL
    })


@login_required
@level_required(REQUIRED_LEVEL +1)
def all(request):
    success = ''
    error = ''
    if request.GET.get('success', '') == '1':
        success = message.STEP_SUCCESS_MSG
    if request.GET.get('error', '') == '1':
        error = message.STEP_ERROR_MSG
    elif request.GET.get('error', '') == '2':
        app_id = request.GET.get('id')
        error = "Loan application with No " + app_id + " has already submitted for this inquiry!!!"
    else:
        error = request.GET.get('error', '')
    user = auth.get_user(request)
    applications = models.VeloceApplication.objects.filter(user=user).order_by('-id')
    return TemplateResponse(request, 'veloce/application/list.html', {
        'applications': applications,
        'success': success,
        'error': error,
        'pending_application': False
    })


@login_required
@level_required(REQUIRED_LEVEL + 1)
def delete(request, app_id):
    user = auth.get_user(request)
    if request.method == 'POST':
        try:
            application = models.VeloceApplication.objects.get(pk=app_id)
        except:
            return redirect('list-application')
        modules = MODULE_MAP[application.application_type]
        if application.current_step > len(modules):
            return redirect('list-application')
        application.delete()

    return redirect('list-application')


@login_required
@level_required(REQUIRED_LEVEL + 1)
def view(request, app_id):
    user = auth.get_user(request)
    try:
        application = models.VeloceApplication.objects.get(pk=app_id)
    except ObjectDoesNotExist:
        return redirect('list-application')
    modules = MODULE_MAP[application.application_type]

    show_forms = []
    for model, form in modules:
        instances = model.objects.filter(application=application)
        instance = instances.get() if len(instances) else None

        new_form = form(instance=instance, label_suffix='')
        forms.utils.disable_fields(new_form)
        show_forms.append(new_form)

    return TemplateResponse(request, 'veloce/application/view.html', {
        'forms': show_forms,
        'hidden': ['agreement']
    })


def ifsc_api(request):
    ifsc_code = request.GET.get('ifsc_code', None)
    url = 'https://ifsc.razorpay.com/' + ifsc_code
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text
    else:
        data = ''
    return JsonResponse(data, safe=False)


@login_required
@level_required(REQUIRED_LEVEL + 1)
def get_bill_info(request, application_type, inq_id):
    try:
        user = auth.get_user(request)
        if user.profile.account_type == 3:
            return redirect('home')
        else:
            app = models.VeloceApplication.objects.filter(inquiry_id=inq_id)
            if app.count() > 0:
                return redirect('/application/list?error=2&id=' + str(app[0].id) + '')
            else:
                application_type = enums.ApplicationType.LOAN.value
                app = models.VeloceApplication(
                    user=user,
                    application_type=application_type,
                    inquiry_id=inq_id
                )
                app.save()
                return redirect('step-application', app.pk, 1)
    except Exception as e:
        print(e, "*************************************************")
        return redirect('home')


@login_required
def get_application1_data(request):
    try:
        app_id = int(request.GET['app_id'])
        get_inq_id = models.VeloceApplication.objects.get(id=app_id)
        get_bill_info = models.VeloceBooksale.objects.using('marketplace').get(inquiry_id=get_inq_id.inquiry_id)
        if get_bill_info.dealers_given_finance_scheme:
            if get_bill_info.dealers_given_finance_scheme.end_date > get_inq_id.created_at:
                dealers_given_finance_scheme = str(
                    get_bill_info.dealers_given_finance_scheme.rate_of_interest) + "%, " + str(
                    get_bill_info.dealers_given_finance_scheme.tenure) + " months"
                finance = True
            else:
                dealers_given_finance_scheme = 0
                finance = False
        else:
            dealers_given_finance_scheme = 0
            finance = False
        borrower_email = get_bill_info.inquiry.inquiry_by.email
        billing_party_name = get_bill_info.billing_party_name
        bill_amount = get_bill_info.bill_amount
        context = {
            "status": True,
            'coborrower_email': get_inq_id.user.email,
            'borrower_email': borrower_email,
            'bill_no': get_bill_info.bill_no,
            'bill_amount': int(bill_amount),
            'bill_date': get_bill_info.bill_date,
            'billing_party_name': billing_party_name,
            'inquired_by': get_bill_info.inquired_by,
            'dealers_given_finance_scheme': dealers_given_finance_scheme,
            "finance": finance
        }
        return JsonResponse(context)
    except Exception as e:
        print(e)
        context = {
            'status': False,
            'msg': str(e)
        }
        return JsonResponse(context)


@login_required
def get_total_emi(request):
    try:
        # import numpy
        import numpy_financial as npf
        app_id = int(request.GET['app_id'])
        required_loan_amount = int(request.GET['required_loan_amount'])
        get_inq_id = models.VeloceApplication.objects.get(id=app_id)
        get_bill_info = models.VeloceBooksale.objects.using('marketplace').get(inquiry_id=get_inq_id.inquiry_id)
        if get_bill_info.dealers_given_finance_scheme:
            interest_val = (get_bill_info.dealers_given_finance_scheme.rate_of_interest / 12) / 100
            total_emi = npf.pmt(interest_val, get_bill_info.dealers_given_finance_scheme.tenure, -required_loan_amount, 0,0)
        else:
            total_emi = 0.00
        context = {
            "status": True,
            'total_emi': round(total_emi, 2)
        }
        return JsonResponse(context)
    except Exception as e:
        context = {
            'status': False,
            'msg': str(e)
        }
        return JsonResponse(context)

@login_required
@level_required(REQUIRED_LEVEL + 1)
def pending_submission(request):
    success = ''
    error = ''
    if request.GET.get('success', '') == '1':
        success = message.STEP_SUCCESS_MSG
    if request.GET.get('error', '') == '1':
        error = message.STEP_ERROR_MSG
    elif request.GET.get('error', '') == '2':
        app_id = request.GET.get('id')
        error = "Loan application with No " + app_id + " has already submitted for this inquiry!!!"
    else:
        error = request.GET.get('error', '')
    user = auth.get_user(request)
    applications = models.VeloceApplication.objects.filter(user=user).order_by('-id')
    return TemplateResponse(request, 'veloce/application/list.html', {
        'applications': applications,
        'success': success,
        'error': error,
        'pending_application': True
    })

def get_finance_scheme_details(request):
    bill_no = int(request.GET['bill_no'])
    borrower_email = request.GET['borrower_email']
    app_data = models.ApplicationStep1.objects.get(bill_no=bill_no, borrower_email=borrower_email)
    print(app_data)
    context = {
        'status': True,
        'bill_amount': app_data.bill_amount,
        'down_payment': app_data.down_payment,
        'loan_amount': app_data.required_loan_amount,
        'tenure_roi': app_data.dealers_given_finance_scheme,
        'emi': app_data.current_loan_emi,
    }
    return JsonResponse(context)