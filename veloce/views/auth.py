from django.conf import settings
from django.shortcuts import redirect
from veloce import methods


def logout(request):
    methods.auth.logout(request)
    next_url = request.build_absolute_uri("/")
    return redirect(settings.OAUTH_URL + "/accounts/logout?next=" + next_url)
