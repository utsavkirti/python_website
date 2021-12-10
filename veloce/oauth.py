from social_core.backends.oauth import BaseOAuth2
from urllib.parse import urlencode
from veloce.models import Profile
from django.conf import settings
import requests
import json

OAUTH_URL = settings.OAUTH_URL


class VeloceOAuth2(BaseOAuth2):
    name = 'vauth'
    AUTHORIZATION_URL = f'{OAUTH_URL}/o/authorize'
    ACCESS_TOKEN_URL = f'{OAUTH_URL}/o/token/'
    ACCESS_TOKEN_METHOD = 'POST'
    STATE_PARAMETER = False
    REDIRECT_STATE = False
    SCOPE_SEPARATOR = ','
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires'),
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('modules', 'modules')
    ]

    def get_user_id(self, details, response):
        return details.get('username')

    def get_username(self, strategy, details, backend, user=None, *args, **kwargs):
        return details.get('username')

    def get_user_details(self, response):
        return {
            'username': response.get('login'),
            'email': response.get('email') or '',
            'first_name': response.get('first_name'),
            'last_name': response.get('last_name'),
            'modules': response.get('modules')
        }

    def user_data(self, access_token, *args, **kwargs):
        url = f'{OAUTH_URL}/accounts/info/'
        return self.get_json(url, headers={
            'Authorization': 'Bearer ' + access_token
        })


def save_profile(backend, user, response, *args, **kwargs):
    if hasattr(user, 'profile'):
        profile = user.profile
    else:
        profile = Profile(user=user)

    modules = response.get("modules")
    max_level = max([m['level'] for m in modules])

    i = -1
    remaining_modules = []
    while i < max_level + 1 and len(remaining_modules) == 0:
        i += 1
        remaining_modules = [m for m in modules if m['level'] <= i and not m['completed']]
    profile.completion_level = i-1

    i = -1
    unverified_modules = []
    while i < max_level + 1 and len(unverified_modules) == 0:
        i += 1
        unverified_modules = [m for m in modules if m['level'] <= i and not m['verified']]
    profile.verification_level = i-1

    profile.is_complete = profile.completion_level >= Profile.MIN_LEVEL
    profile.is_verified = profile.verification_level >= Profile.MIN_LEVEL
    profile.account_type = response.get("account_type")
    profile.save()


def refetch_profile(user):
    url = f'{OAUTH_URL}/accounts/info/'
    response = json.loads(requests.get(url, headers={
        'Authorization': 'Bearer ' + user.social_auth.get().extra_data['access_token']
    }).text)
    save_profile(None, user, response)
