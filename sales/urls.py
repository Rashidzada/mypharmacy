from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('api/search/', views.product_search_api, name='product_search_api'),
    path('api/create/', views.create_sale_api, name='create_sale_api'),
    path('invoice/<int:invoice_id>/print/', views.invoice_print, name='invoice_print'),
    path('invoice/<int:invoice_id>/return/', views.sales_return_create, name='sales_return_create'),
]
