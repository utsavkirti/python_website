import re
import magic, requests, json
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, HttpResponse, Http404
from django.core.files.storage import default_storage
from django.template.response import TemplateResponse
from veloce import models, methods, enums
from django.conf import settings
from veloce.decorators import level_required

def index(request):
    if request.user.is_authenticated:
        if request.user.profile.account_type == 3:
            return redirect('admin-borrower-applications')
        else:           
            # return TemplateResponse(request, 'veloce/application/list.html',{})
            return TemplateResponse(request, "veloce/content/home.html", {})
            # return redirect('list-application')
    else:
        return TemplateResponse(request, "veloce/content/home.html", {})

            
@login_required
def overview(request):
    user = auth.get_user(request)
    if not user.profile.is_complete:
        return redirect('incomplete-profile')
    return TemplateResponse(request, "veloce/overview.html", {
        "user": methods.auth.veloce_user(user)
    })


# @login_required
# def incomplete_profile(request, level=models.profile.Profile.MIN_LEVEL):
#     modules = request.user.social_auth.get().extra_data['modules']
#     incomplete = []
#     status = ''
#     data = {'uid': request.user.email}
#     # res = requests.get('http://innovations.veloce.market/check-updated-module-approved/', params=data).text
#     res = requests.get('http://192.168.0.20:7004/check-updated-module-approved/', params=data).text
#     response = json.loads(res)
#     response['incomplete_level'] = list(set(response['incomplete_level']))
#     response['not_verified_level'] = list(set(response['not_verified_level']))
#     if response['status'] == False:
#         data = response
#     if len(data['incomplete_level']) <= 0 and len(data['not_verified_level']) <= 0:
#         return redirect('overview')
#     else:
#         incomplete = [modules[m] for m in data['incomplete_level']]
#     if len(incomplete) <= 0:
#         status = 'not verified'
#         # incomplete = [m for m in modules if m['level'] <= level and not m['verified']]
#     else:
#         status = 'incomplete'
#     return TemplateResponse(
#         request,
#         "veloce/profile/incomplete.html",
#         {'incomplete': incomplete, "status": status}
#     )

@login_required
def incomplete_profile(request, level=models.profile.Profile.MIN_LEVEL):
    modules = request.user.social_auth.get().extra_data['modules']
    incomplete = []
    status = ''
    data = {'uid': request.user.email}
    res = requests.get('http://innovations.veloce.market/check-updated-module-approved/', params=data).text
    # res = requests.get('http://192.168.0.20:7004/check-updated-module-approved/', params=data).text
    response = json.loads(res)
    response['incomplete_level'] = list(set(response['incomplete_level']))
    response['not_verified_level'] = list(set(response['not_verified_level']))
    if response['status'] == False:
        data = response

    if len(data['incomplete_level']) <= 0 and len(data['not_verified_level']) <= 0:
        return redirect('overview')
    else:
        incomplete = [modules[m] for m in data['incomplete_level']]

    if len(incomplete) <= 0:
        status = 'not verified'
        # incomplete = [m for m in modules if m['level'] <= level and not m['verified']]
    else:
        status = 'incomplete'
    return TemplateResponse(
        request,
        "veloce/profile/incomplete.html",
        {'incomplete': incomplete, "status": status}
    )

@login_required
def incomplete_admin_approval(request, level=models.profile.Profile.MIN_LEVEL):
    modules = request.user.social_auth.get().extra_data['modules']
    incomplete = [m for m in modules if m['level'] <= level and not m['verified']]
    return TemplateResponse(
        request,
        "veloce/profile/incomplete.html",
        {'incomplete': incomplete}
    )


@login_required
def download(request):
    path = request.GET.get("path")
    if not path:
        raise Http404("Could not find the requested image.")
    if not re.match(f'^media/user\_[0-9]+/[a-zA-Z\_0-9\-]+\.(png|pdf|jpg|jpeg)$', path):
        raise Http404("Could not find the requested image.")

    path_parts = path.split('/')
    user_id = int(path_parts[1].split('_')[1])

    user = auth.get_user(request)
    if user_id == user.id or user.is_superuser:
        with default_storage.open(path, "rb") as f:
            data = f.read()
            mime = magic.from_buffer(data, mime=True)
            return HttpResponse(data, content_type=mime)
    return redirect('/')


@login_required
def edit_profile(request):
    response = redirect(settings.OAUTH_URL + "/overview")
    access_token = request.user.social_auth.get().extra_data['access_token']
    response['Authorization'] = 'Bearer ' + access_token
    return response


def about_veloce(request):
    return TemplateResponse(request, "veloce/content/about-veloce.html", {})


def about_veloce_fintech(request):
    return TemplateResponse(request, "veloce/content/about-veloce-fintech.html", {})


def how_veloce_fintech_works(request):
    return TemplateResponse(request, "veloce/content/how-veloce-market-works.html", {})


def FAQ_ftr(request):
    return TemplateResponse(request, "veloce/content/faqs-ftr.html", {})


def loans_ftr(request):
    return TemplateResponse(request, "veloce/content/loans-ftr.html", {})


def loans_eligibility(request):
    return TemplateResponse(request, "veloce/content/loans-eligibility.html", {})


def type_of_loans(request):
    return TemplateResponse(request, "veloce/content/type-of-loans.html", {})


def loans_rates_fees(request):
    return TemplateResponse(request, "veloce/content/loans-rates-fees.html", {})


def finance_with_us(request):
    return TemplateResponse(request, "veloce/content/finance-with-us.html", {})


def finance_eligibility(request):
    return TemplateResponse(request, "veloce/content/finance-eligibility.html", {})


def veloce_work_content(request):
    return TemplateResponse(request, "veloce/content/veloce-work-content.html", {})


def testimonials(request):
    return TemplateResponse(request, "veloce/content/testimonials.html", {})


def contact_us(request):
    return TemplateResponse(request, "veloce/content/contact-us.html", {})


def investing(request):
    return TemplateResponse(request, "veloce/content/investing.html", {})


def borrowing(request):
    return TemplateResponse(request, "veloce/content/borrowing.html", {})


def FAQ(request):
    return TemplateResponse(request, "veloce/content/faq.html", {})


def privacy_policy(request):
    return TemplateResponse(request, "veloce/content/privacy-policy.html", {})


def terms_of_use(request):
    return TemplateResponse(request, "veloce/content/terms-of-use-new.html", {})


def grievance_redressal(request):
    return TemplateResponse(request, "veloce/content/grievance-redressal.html", {})


def fair_practices_code(request):
    return TemplateResponse(request, "veloce/content/fair-practices-code.html", {})


def disclaimer(request):
    return TemplateResponse(request, "veloce/content/disclaimer.html", {})


def support(request):
    return TemplateResponse(request, "veloce/content/support.html", {})


def legal(request):
    return TemplateResponse(request, "veloce/content/legal.html", {})


def careers(request):
    return TemplateResponse(request, "veloce/content/careers.html", {})
