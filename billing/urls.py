from django.urls import path

from . import views

urlpatterns = [
    path('', views.partner_billing_statements, name='billing_statements'),
    path('statement/<int:statement_id>/', views.partner_billing_statement_details, name='statement_details'),
    path('not_on_statement/', views.partner_billing_not_on_statement, name='billing_not_on_statement'),
    path('log_payment/', views.log_payment, name='staff_log_payment'),
    path('log_payout/', views.log_payout, name='staff_log_payout'),
    path('log_other/', views.log_other, name='staff_log_other'),

]
