from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.cash_summary, name='cash_summary'),
    path('summary/export/daily/', views.export_daily_records, name='cash_summary_export_daily'),
    path('summary/export/month/', views.export_monthly_records, name='cash_summary_export_month'),
    path('summary/export/year/', views.export_yearly_summary, name='cash_summary_export_year'),
]
