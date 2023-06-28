from django.urls import path

from . import views

urlpatterns = [
    path('', views.sales_overview, name='partner_sales_overview'),

]
