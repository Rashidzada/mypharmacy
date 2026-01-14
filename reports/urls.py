from django.urls import path
from . import views

urlpatterns = [
    path('expiry-alerts/', views.expiry_alerts, name='expiry_alerts'),
    path('daily-sales/', views.daily_sales, name='daily_sales'),
]
