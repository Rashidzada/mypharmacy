from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # path("seed_data/", views.seed_data, name="seed_data"),
   
]
