from datetime import datetime
from veloce import models
import numpy
from django.conf import settings
from instamojo_wrapper import Instamojo


def save_application_step(form, application, borrower, step):
    application_step = form.save(commit=False)
    application_step.application = application
    application_step.save()
    if borrower:
        my_cur_app_form = models.ApplicationStep1.objects.get(pk=application_step.id)
        my_cur_app_form.borrower_email = borrower
        my_cur_app_form.save()
    application.current_step = max(step + 1, application.current_step)
    application.updated_at = datetime.now()
    application.save()


# def payment_api(request, app_id, step):
#     api = Instamojo(api_key=settings.API_KEY, auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')
#     response = api.payment_request_create(
#         amount='10',
#         purpose='Veloce Loan Application Fees',
#         send_email=True,
#         email="ajay@gmail.com",
#         redirect_url="https://velocefintech.com/application/{0}/step{1}".format(app_id, step)
#     )
#     return response

def payment_api(request, app_id, step):
    api = Instamojo(api_key=settings.API_KEY, auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')
    response = api.payment_request_create(
        amount='10',
        purpose='Beagle Loan Application Fees',
        send_email=True,
        email="beaglebazaar@gmail.com",
        redirect_url="http://192.168.0.20:7003/application/{0}/step{1}".format(app_id, step)
    )
    return response

def emi_calculator(roi, amount, tenure):
    roi = (roi / 12) / 100
    emi = numpy.pmt(roi, tenure, -amount, 0, 0)
    emi = round(emi, 2)
    return emi
