from django.contrib import admin
from .models import Supplier, PurchaseInvoice, PurchaseItem

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone')
    search_fields = ('name', 'phone')

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ('product', 'batch_number', 'expiry_date', 'quantity', 'unit_price', 'discount_percentage', 'tax_percentage', 'total_amount')
    readonly_fields = ('total_amount',)

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier', 'date', 'grand_total')
    list_filter = ('supplier', 'date')
    search_fields = ('invoice_number', 'supplier__name')
    inlines = [PurchaseItemInline]
