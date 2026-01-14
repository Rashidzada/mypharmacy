from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
from .models import SalesInvoice, SaleItem, Customer
from inventory.models import Product, Batch
from django.db.models import Q

def pos_view(request):
    customers = list(Customer.objects.values('id', 'name', 'phone'))
    customers_json = json.dumps(customers)
    context = {'customers_json': customers_json}
    return render(request, 'sales/pos.html', context)

def invoice_print(request, invoice_id):
    invoice = get_object_or_404(SalesInvoice.objects.prefetch_related('items'), id=invoice_id)
    return render(request, 'sales/invoice_print.html', {'invoice': invoice})

def product_search_api(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(brand__name__icontains=query) |
        Q(category__name__icontains=query)
    )[:20]
    
    results = []
    for p in products:
        # Get available stock
        batches = p.batches.filter(quantity__gt=0).order_by('expiry_date')
        total_qty = sum(b.quantity for b in batches)
        
        # Get price (use latest purchase price or manual sale price)
        # For simplicity, using the sale_price of the first available batch or a default
        price = 0
        if batches.exists():
            price = batches.first().sale_price or 0
        
        results.append({
            'id': p.id,
            'name': p.name,
            'brand': p.brand.name,
            'stock': total_qty,
            'price': float(price),
            'tax': float(p.tax_percentage)
        })
    
    return JsonResponse({'results': results})

@csrf_exempt
@transaction.atomic
def create_sale_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received sale data:", data) # Debug log
            
            # Handle Customer
            customer_name = data.get('customer_name')
            customer_phone = data.get('customer_phone')
            customer = None
            if customer_phone:
                customer, created = Customer.objects.get_or_create(
                    phone=customer_phone,
                    defaults={'name': customer_name, 'address': ''}
                )
                if not created and customer_name:
                     customer.name = customer_name
                     customer.save()
            elif customer_name:
                 customer = Customer.objects.create(name=customer_name)

            # Create Invoice
            invoice = SalesInvoice.objects.create(
                customer=customer,
                payment_mode=data.get('payment_mode', 'CASH'),
                discount_percentage=data.get('discount_percentage', 0),
                discount_amount=data.get('discount_amount', 0),
                sub_total=data.get('sub_total', 0),
                tax_amount=data.get('tax_total', 0),
                grand_total=data.get('grand_total', 0),
                amount_paid=data.get('amount_paid', 0),
                change_amount=data.get('change_amount', 0)
            )
            
            items_data = data.get('items', [])
            for item in items_data:
                # CHECK IF MANUAL ITEM
                if item.get('type') == 'manual':
                     SaleItem.objects.create(
                        invoice=invoice,
                        product=None,
                        batch=None,
                        item_name=item['name'],
                        quantity=int(item['quantity']),
                        unit_price=item['price'],
                        total_amount=float(item['quantity']) * float(item['price'])
                     )
                     continue

                # NORMAL INVENTORY ITEM
                product = Product.objects.get(id=item['product_id'])
                qty_needed = int(item['quantity'])
                
                # FIFO Strategy: Find batches
                batches = product.batches.filter(quantity__gt=0).order_by('expiry_date')
                
                qty_remaining = qty_needed
                
                for batch in batches:
                    if qty_remaining <= 0:
                        break
                    
                    take_qty = min(batch.quantity, qty_remaining)
                    
                    # Create Sale Item for this batch
                    SaleItem.objects.create(
                        invoice=invoice,
                        product=product,
                        batch=batch,
                        quantity=take_qty,
                        unit_price=item['price'],
                        discount_percentage=item.get('discount_percentage', 0),
                        discount_amount=item.get('discount_amount', 0),
                        tax_amount=item.get('tax_amount', 0),
                        total_amount=item.get('total', 0) # This might need splitting if multiple batches
                    )
                    
                    # Updates stock
                    batch.quantity -= take_qty
                    batch.save()
                    
                    qty_remaining -= take_qty
                
                # Handle case where stock was insufficient (Negative stock? Or just error?)
                # Requirement said: "Products can be sold even if: Not in inventory"
                if qty_remaining > 0:
                     # Create a dummy or separate logic for negative stock. 
                     # For now, we just sell what we have or error?
                     # User explicitly said "even if Not in inventory".
                     # So we might need a dummy batch or allow negative on the last batch.
                     # Let's pick the last batch and go negative.
                     if batches.exists():
                         last_batch = batches.last()
                         SaleItem.objects.create(
                            invoice=invoice,
                            product=product,
                            batch=last_batch,
                            quantity=qty_remaining,
                            unit_price=item['price']
                         )
                         last_batch.quantity -= qty_remaining
                         last_batch.save()
            
            return JsonResponse({'status': 'success', 'invoice_id': invoice.id})
        except Exception as e:
            import traceback
            traceback.print_exc() # Print full stack trace
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
