from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier, PurchaseInvoice
from .forms import SupplierForm, PurchaseInvoiceForm, PurchaseItemFormSet
from django.contrib import messages
from inventory.models import Batch

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'purchases/supplier_list.html', {'suppliers': suppliers})

def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'purchases/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

def purchase_create(request):
    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.invoice = invoice
                # Create Batch Logic
                batch = Batch.objects.create(
                    product=item.product,
                    batch_number=item.batch_number,
                    expiry_date=item.expiry_date,
                    purchase_price=item.unit_price,
                    sale_price=item.sale_price,
                    quantity=item.quantity
                )
                item.batch = batch
                item.save()
            messages.success(request, 'Purchase Invoice saved and Stock updated.')
            return redirect('dashboard') # Or purchase list
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
    else:
        form = PurchaseInvoiceForm()
        formset = PurchaseItemFormSet()
    return render(request, 'purchases/purchase_form.html', {'form': form, 'formset': formset})
