from django.contrib import admin
from .models import Customer, SalesInvoice, SaleItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ('product', 'batch', 'quantity', 'unit_price', 'total_amount')
    readonly_fields = ('total_amount',)

@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'date', 'grand_total', 'payment_mode')
    list_filter = ('date', 'payment_mode')
    search_fields = ('invoice_number',)
    inlines = [SaleItemInline]
