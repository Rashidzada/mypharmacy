from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.cash_summary, name='cash_summary'),
]
