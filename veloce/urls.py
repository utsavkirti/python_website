from django.urls import path

from veloce import views

urlpatterns = [
    path('', views.home.index, name='home'),
    path('accounts/profile/', views.home.index, name='profile'),
    path('auth/logout', views.auth.logout, name='logout'),

    path('overview', views.home.overview, name='overview'),
    path('incomplete-profile', views.home.incomplete_profile, name='incomplete-profile'),
    path('incomplete-profile/<int:level>', views.home.incomplete_profile, name='incomplete-profile'),
    path('incomplete_admin_approval', views.home.incomplete_admin_approval, name='incomplete_admin_approval'),
    path('edit-profile', views.home.edit_profile, name='edit-profile'),
    path('download', views.home.download, name='download'),

    # My Applications
    path('application/list', views.application.all, name='list-application'),
    path('pending-application', views.application.pending_submission, name='pending-application'),
    path('application/new/<str:application_type>', views.application.new, name='new-application'),###done
    path('application/bill/new/<str:application_type>/<int:inq_id>', views.application.get_bill_info, name='bill-info'),
    path('application/<int:app_id>', views.application.view, name='view-application'),
    path('application/<int:app_id>/step<int:step>', views.application.step, name='step-application'),
    path('application/<int:app_id>/delete', views.application.delete, name='delete-application'),
    path('bank/ifsc/', views.application.ifsc_api, name='ifsc-api'),
    path('get-application-info/', views.application.get_application1_data, name='get_application1_data'),
    path('calculate-total-emi/', views.application.get_total_emi, name='get_total_emi'),

    # Loans
    path('my-loans-application/', views.loans.my_loans_app, name='my-loans-app'),
    path('my-accepted-loans-application/', views.loans.my_accepted_loans_app, name='my_accepted_loans_app'),
    path('my-loans/<int:app_id>', views.loans.my_loans, name='my-loans'),
    path('loans', views.loans.loans, name='loans'),
    path('view-loan/<int:loan_id>', views.loans.view_loan, name='view-loan'),
    path('fund/<int:loan_id>', views.loans.fund_loan, name='fund-loan'),
    path('disburse/<int:loan_id>', views.loans.disburse_loan, name='disburse-loan'),

    # ravi
    path('dashboard/',views.loans.user_dashboard,name='user_dashboard'),

    # Content pages
    path('about-veloce', views.home.about_veloce, name='about-veloce'),
    path('about-veloce-fintech', views.home.about_veloce_fintech, name='about-veloce-fintech'),
    path('how-veloce-fintech-works', views.home.how_veloce_fintech_works, name='how-veloce-fintech-works'),
    path('testimonials', views.home.testimonials, name='testimonials'),
    path('contact-us', views.home.contact_us, name='contact_us'),
    path('faqs-ftr', views.home.FAQ_ftr, name='faqs-ftr'),
    path('veloce-work-content', views.home.veloce_work_content, name='veloce-work-content'),
    path('investing', views.home.investing, name='investing'),
    path('borrowing', views.home.borrowing, name='borrowing'),
    path('FAQ', views.home.FAQ, name='FAQ'),
    path('loans-ftr', views.home.loans_ftr, name='loans_ftr'),
    path('loans-eligibility', views.home.loans_eligibility, name='loans_eligibility'),
    path('type-of-loans', views.home.type_of_loans, name='type_of_loans'),
    path('loans-rates-fees', views.home.loans_rates_fees, name='loans_rates_fees'),
    path('finance-with-us', views.home.finance_with_us, name='finance_with_us'),
    path('finance-eligibility', views.home.finance_eligibility, name='finance_eligibility'),
    path('terms-of-use-new', views.home.terms_of_use, name='terms-of-use-new'),
    path('privacy-policy', views.home.privacy_policy, name='privacy-policy'),
    path('grievance-redressal', views.home.grievance_redressal, name='grievance_redressal'),
    path('fair-practices-code', views.home.fair_practices_code, name='fair_practices_code'),
    path('disclaimer', views.home.disclaimer, name='disclaimer'),
    path('legal', views.home.legal, name='legal'),
    path('careers', views.home.careers, name='careers'),
    path('support', views.home.support, name='support'),

    # Admin Applications
    path('lender/borrower-applications', views.admin.borrower_applications, name='admin-borrower-applications'),
    path('lender/review-application/<int:app_id>', views.admin.review_application, name='admin-review-application'),
    path('lender/reject-application/<int:app_id>', views.admin.reject_application, name='admin-reject-application'),
    path('lender/approve-application/<int:app_id>', views.admin.approve_application, name='admin-approve-application'),
    path('calculate-disbursement-amount/', views.admin.calculate_disbursement_amount, name='calculate_disbursement_amount'),
    path('lender/borrower-applications-disbursement/', views.loans.my_approved_loans, name='my_approved_loans'),
    path('lender/my-disburse-applications/', views.loans.my_disbursement_loans, name='my_disbursement_loans'),
    path('get-finance-scheme-details/', views.application.get_finance_scheme_details, name='get-finance-scheme-details'),
    path('display-user-details-to-lender/', views.admin.display_user_details_to_lender, name='display-user-details-to-lender'),


]
