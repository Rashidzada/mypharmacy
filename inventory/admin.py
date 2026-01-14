from django.contrib import admin
from .models import Category, Brand, Product, Batch

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'company', 'tax_percentage')
    list_filter = ('category', 'brand', 'company')
    search_fields = ('name', 'brand__name', 'company')

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('product', 'batch_number', 'expiry_date', 'quantity', 'purchase_price', 'sale_price')
    list_filter = ('expiry_date',)
    search_fields = ('product__name', 'batch_number')
