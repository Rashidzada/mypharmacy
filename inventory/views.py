from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Product, Batch
from .forms import ProductForm, BatchForm
from django.contrib import messages

def product_list(request):
    query = (request.GET.get('q') or '').strip()
    products = Product.objects.all().select_related('brand', 'category')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        )
    return render(request, 'inventory/product_list.html', {'products': products, 'query': query})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add Product'})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product'})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

def add_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.product = product
            batch.save()
            messages.success(request, f'Stock added to {product.name} successfully.')
            return redirect('product_list')
    else:
        form = BatchForm()
    return render(request, 'inventory/batch_form.html', {'form': form, 'product': product})
