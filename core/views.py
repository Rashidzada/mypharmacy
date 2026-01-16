from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from sales.models import SalesInvoice
from inventory.models import Product
from reports.utils.expiry_alerts import get_expiry_alert_counts

def dashboard(request):
    today = timezone.now().date()
    
    # 1. Today's Sales
    todays_sales = SalesInvoice.objects.filter(date__date=today).aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    
    # 2. Low Stock (e.g., total quantity < 10)
    # This is complex in aggregation, so doing Python side for simplicity in MVP
    products = Product.objects.all().prefetch_related('batches')
    low_stock_count = 0
    for p in products:
        stock = sum(b.quantity for b in p.batches.all())
        if stock < 10: # Threshold
            low_stock_count += 1
            
    expiry_counts = get_expiry_alert_counts(today=today)
    expired_count = expiry_counts["expired"]
    
    # 4. Total Products
    total_products = Product.objects.count()
    
    # Recent Sales
    recent_sales = SalesInvoice.objects.order_by('-date')[:5]

    context = {
        'todays_sales': todays_sales,
        'low_stock': low_stock_count,
        'expired': expired_count,
        'total_products': total_products,
        'recent_sales': recent_sales,
        'expiry_counts': expiry_counts,
        'show_expiry_widget': request.user.is_authenticated
        and (request.user.is_staff or request.user.has_perm('reports.view_reports')),
    }
    return render(request, 'core/dashboard.html', context)
