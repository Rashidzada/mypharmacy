from django import forms
from decimal import Decimal
from .models import Supplier, PurchaseInvoice, PurchaseItem
from django.forms import inlineformset_factory

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        fields = ['supplier', 'invoice_number', 'date', 'note']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = [
            'product', 'batch_number', 'expiry_date', 'quantity',
            'unit_price', 'sale_price', 'discount_percentage', 'tax_percentage',
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount_percentage'].required = False
        self.fields['tax_percentage'].required = False
        self.fields['discount_percentage'].initial = Decimal('0')
        self.fields['tax_percentage'].initial = Decimal('0')

    def clean_discount_percentage(self):
        value = self.cleaned_data.get('discount_percentage')
        return value if value is not None else Decimal('0')

    def clean_tax_percentage(self):
        value = self.cleaned_data.get('tax_percentage')
        return value if value is not None else Decimal('0')

PurchaseItemFormSet = inlineformset_factory(
    PurchaseInvoice, PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
)
