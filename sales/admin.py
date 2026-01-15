from django.contrib import admin
from .models import Customer, SalesInvoice, SaleItem, SalesReturn, SalesReturnItem

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

class SalesReturnItemInline(admin.TabularInline):
    model = SalesReturnItem
    extra = 0
    fields = ('sale_item', 'quantity', 'unit_refund', 'total_amount')
    readonly_fields = ('total_amount',)

@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'date', 'refund_amount')
    list_filter = ('date',)
    search_fields = ('invoice__invoice_number',)
    inlines = [SalesReturnItemInline]
