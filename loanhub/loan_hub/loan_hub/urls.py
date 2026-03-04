"""
URL configuration for loan_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *
from .views import *
from . import views



urlpatterns = [
    path('', login_view, name='login'),
    path('admin/', admin.site.urls),
    path('viewtransactions/<int:loan_id>/', mtl_collection_view, name='mtl_collection'),
    path('adduser/', add_user, name='adduser'),
    path('loans/', loans_view, name='loans'),
    path('deposits/', deposits_view, name='deposits'),
    # path('others/', others_view, name='others'),
    path('closed-loans/', closed_loans_view, name='closed_loans'),
    path('addloan/', add_loan, name='addloan'),
    path('loan-transactions-detail/<int:loan_id>/<str:month>/', loan_transactions_detail, name='loan_transactions_detail'),
    path('cash_book/', cash_book, name='cash_book'),
    path('add-cash/', add_cash_view, name='add_cash'),
    path('mtl-collection/', mtl_collection_view, name='mtl_collection'),
    path('intrest_rate/', interest_rate_view, name='intrest_rate'),
    path('update-payment/', update_payment, name='update_payment'),
    path('Update_intrest_rate/', Update_intrest_rate, name='Update_intrest_rate'),
    path('submit_new_table/', submit_new_table, name='submit_new_table'),
    path('search-codes/', search_user_codes, name='search_user_codes'),
    # path('reports/',reports_view, name='reports'),

    # path('reports/download-receipts/', download_receipts, name='download_receipts'),
    # path('reports/download-payments/', download_payments, name='download_payments'),
    path('reports/', reports_view, name='reports'),

     path('download-users/', download_users, name='download_users'),


#  new urls...donot change above by TARUN AMARANENI
   path('download-user-report/',download_user_report, name='download_user_report'),

   path("download-reports/",download_reports, name="download_reports"),

   path("download-users/", download_users, name="download_users"),
   
   path("cash-entry/", cash_entry_view, name="cash_entry"),  # new path and name
   

    path('download-reports/', download_reports, name='download_reports'),
    path('reports-list/', reports_list_view, name='reports_list'),
    path('download-payments/', download_payments, name='download_payments'),
    path('download-receipts/', download_receipts, name='download_receipts'),



    # DOWNLOAD (FILTERED BY LOAN TYPE)
path('download-payments/', download_payments, name='download_payments'),
path('download-payments/<str:loan_type>/', download_payments, name='download_payments_by_type'),

path('download-receipts/', download_receipts, name='download_receipts'),
path('download-receipts/<str:loan_type>/', download_receipts, name='download_receipts_by_type'),



path('download-report/<str:report_type>/<str:view_mode>/', download_report_view, name='download_report'),



path('download_receipts_dynamic/', download_receipts_dynamic, name='download_receipts_dynamic'),
    path('download_payments_dynamic/', download_payments_dynamic, name='download_payments_dynamic'),


path('search-user/', user_search, name='search_user'),



path("upload-excel/", upload_excel, name="upload_excel"),

path('download-sample-excel/', download_sample_excel, name='download_sample_excel'),

path('logout/', logout_view, name='logout'),


path('search-user-codes/', search_user_codes, name='search_user_codes'),
path('all-users/', all_users, name='all_users'),



# date @05/01/2026
path('cash-withdrawals/', cash_withdrawals, name='cash_withdrawals'),
path('cash-transfer/', cash_transfer, name='cash_transfer'),




path('others/', others, name='others'),
 path('save-other-cash/', save_other_cash_transaction, name='save_other_cash_transaction'),




# urls.py
path("reports/others/", other_reports_table, name="other_reports_table"),

# new
# urls.py

    # path('others/', others, name='others'),
    path('save-other-cash/', save_other_cash_transaction, name='save_other_cash_transaction'),
    path('fetch-receipts/', fetch_receipts, name='fetch_receipts'),
    path('fetch-payments/',fetch_payments, name='fetch_payments'),



# path('add-loan/', add_loan_view, name='add_loan'),

 path('api/get_user_info/', get_user_info, name='get_user_info'),






path('add-loan/', loans_view, name='add_loan'),  # your main add loan page
    path('api/fetch_users_dropdown/', fetch_users_dropdown, name='fetch_users_dropdown'),


    # path('add-loan/', add_loan_view, name='add_loan'),
    path('api/users-autocomplete/', user_autocomplete, name='user_autocomplete'),





path('users/', users, name='users'),
path('users/edit/<int:id>/', edit_user, name='edit_user'),
path('users/delete/<int:id>/', delete_user, name='delete_user'),

path('loanadd/', loanadd, name='loanadd'),


path('loans/edit/<int:loan_id>/', views.edit_loan, name='edit_loan'),
path("delete-loan/", views.delete_loan, name="delete_loan"),
path("other-cash/edit/<int:id>/", views.edit_other_cash_transaction, name="edit_other_cash"),
path("other-cash/delete/", views.delete_other_cash, name="delete_other_cash"),


path('dashboard/', views.dashboard, name='dashboard'),








path('get-loan/<int:loan_id>/', views.get_loan, name='get_loan'),
path('update-loan/', views.update_loan, name='update_loan'),








# 17 feb 2026
path(
    'loans/<int:loan_id>/repayments/',
    views.loan_repayment_list,
    name='loan_repayment_list'
),


path(
    'loans/<int:loan_id>/repayments/',
    views.loan_repayment_listd,
    name='loan_repayment_listd'
),




  path("loan-transactions/<int:loan_id>/", loan_transactions_view, name="loan_transactions"),
  



  path('api/active-loans/', active_loans_api, name='active_loans_api'),



#   path("download/user/<str:gen_no>/", views.download_user_pdf, name="download_user_pdf"),
path("download/loan/<int:loan_id>/", views.download_loan_pdf, name="download_loan_pdf"),


# Full report (default)
path(
    "download-user-pdf/<str:gen_no>/",
    views.download_user_pdf,
    name="download_user_pdf"
),

# Filtered reports
path(
    "download-user-pdf/<str:gen_no>/<str:report_type>/",
    views.download_user_pdf,
    name="download_user_pdf"
),




# 17 feb 2026
# -------------------------------
    # Loan Repayments (PER LOAN)
    # IMPORTANT: uses loan_id
    # -------------------------------
    path(
        'loans/<int:loan_id>/repayments/',
        views.loan_repayment_list,
        name='loan_repayment_list'
    ),
]






