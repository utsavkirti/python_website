from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from veloce import models
from veloce.enums import AccountType
from veloce.models.profile import Profile
from veloce.oauth import refetch_profile
import requests, json
from django.contrib import messages
from django.utils.safestring import mark_safe


def login_forbidden(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('overview')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def level_required(level=Profile.MIN_LEVEL):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.profile.account_type == 3:
                required_level = level - 1
            else:
                required_level = level
            if request.user.profile.completion_level < required_level or request.user.profile.verification_level < required_level:
                refetch_profile(request.user)
                return redirect('incomplete-profile', level)
            else:
                return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator
