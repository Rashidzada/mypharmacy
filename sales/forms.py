from django import forms
from .models import SalesInvoice

class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
        fields = ['customer', 'payment_mode', 'discount_percentage', 'discount_amount']
