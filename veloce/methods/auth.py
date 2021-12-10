from django.contrib import auth


def veloce_user(user):
    return user.social_auth.get().extra_data


def logout(request):
    auth.logout(request)
