from django.shortcuts import render, redirect, reverse
from django.contrib import auth
from django.conf import settings
from veloce import enums


class MenuItem:
    def __init__(self, url, name, subitem=False):
        self.url = url
        self.name = name
        self.classname = "btn" if not subitem else "btn subitem"


class MenuInjectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        menu = self.generate_menu(request)
        for item in menu:
            if request.get_full_path() == item.url:
                item.classname += " active"
        response.context_data["menu"] = menu
        response.context_data["authenticated"] = request.user.is_authenticated
        return response

    def generate_menu(self, request):
        if request.user.is_authenticated:

            user = auth.get_user(request)

            if user.is_superuser:
                return [
                    MenuItem("#", "Dashboard"),
                ]
            if user.profile.account_type == 3:
                # Admin menu
                return [
                            
                            MenuItem(reverse("admin-borrower-applications"), "Loan Applications"),
                            MenuItem(reverse("admin-borrower-applications") + "?filterBy=0", "Pending Applications", True),
                            MenuItem(reverse("admin-borrower-applications") + "?filterBy=2", "Sanctioned", True),
                            MenuItem(reverse("admin-borrower-applications") + "?filterBy=1", "Rejected", True),
                            MenuItem(reverse("my_approved_loans"), "Accepted By Dealer", True),
                            MenuItem(reverse("my_disbursement_loans"), "Disbursed", True),
                        ]

            return [
                        # MenuItem(reverse('overview'), "Overview"),

                        # MenuItem(settings.OAUTH_URL + "/overview", "Edit Profile", True),
                        # MenuItem(settings.OAUTH_URL + "/accounts/change-password/", "Change Password", True),
                        MenuItem("/", "Home"),
                        MenuItem(reverse('list-application'), "Loan Applications"),
                        # MenuItem(reverse('new-application', args=['loan']), "New Application", True),
                        # MenuItem(reverse('new-application', args=['invoice']), "New Invoice", True),
                        MenuItem(reverse('pending-application'), "Pending Application", True),
                        MenuItem(reverse('my-loans-app'), "Sanctioned", True),
                        MenuItem(reverse('my_accepted_loans_app'), "Accepted", True),
                        # MenuItem(reverse('my-loans'), "Sanctioned Loans", True),
                        MenuItem(reverse('loans'), "Disbursed", True),
                    ]

        # Unauthenticated menu
        return [
                    MenuItem("/", "Home"),

                    # MenuItem(reverse('list-application'), "Loan Applications"),
                    # MenuItem(reverse('pending-application'), "Pending Application", True),
                    # MenuItem(reverse('my-loans-app'), "Sanctioned", True),
                    # MenuItem(reverse('my_accepted_loans_app'), "Accepted", True),
                    # MenuItem(reverse('loans'), "Disbursed", True),

                    # MenuItem(settings.OAUTH_URL + "/accounts/register/", "Register", True),
                    # MenuItem("/login/vauth", "Sign In", True),

                    # MenuItem(reverse('about-veloce'), "About Veloce"),
                    # MenuItem(reverse('veloce-work-content'), "How it works", True),
                    # MenuItem(reverse('investing'), "Investing", True),
                    # MenuItem(reverse('borrowing'), "Borrowing", True),
                    # MenuItem(reverse('FAQ'), "FAQs", True),

                    # MenuItem(reverse('legal'), "Legal"),
                    # MenuItem(reverse('terms-of-use-new'), "Terms of Use", True),
                    # MenuItem(reverse('privacy-policy'), "Our Privacy Policy", True),
                    # MenuItem(reverse('disclaimer'), "RBI Disclaimer", True),

                    # MenuItem(reverse('careers'), "Careers"),
                ]
