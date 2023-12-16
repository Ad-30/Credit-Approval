from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register_customer, name='register_customer'),
    path('check-eligibility/', views.check_eligibility, name='check_eligibility'),
    path('create-loan/', views.create_loan, name='create_loan'),
    path('loan/<int:loan_id>/', views.loan_details, name='loan-details'),
    path('view-loans/<int:customer_id>/', views.view_loans_by_customer, name='view-loans-by-customer'),
]

