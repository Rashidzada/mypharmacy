from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from inventory.models import Batch
from sales.models import SalesInvoice, SalesReturn

def expiry_alerts(request):
    today = timezone.now().date()
    
    # Thresholds
    red_limit = today + timedelta(days=45)
    yellow_limit = today + timedelta(days=90)
    green_limit = today + timedelta(days=180)
    
    # Queries
    expired = Batch.objects.filter(expiry_date__lt=today, quantity__gt=0)
    
    red_zone = Batch.objects.filter(
        expiry_date__gte=today, 
        expiry_date__lte=red_limit, 
        quantity__gt=0
    )
    
    yellow_zone = Batch.objects.filter(
        expiry_date__gt=red_limit, 
        expiry_date__lte=yellow_limit, 
        quantity__gt=0
    )
    
    green_zone = Batch.objects.filter(
        expiry_date__gt=yellow_limit, 
        expiry_date__lte=green_limit, 
        quantity__gt=0
    )
    
    context = {
        'expired': expired,
        'red_zone': red_zone,
        'yellow_zone': yellow_zone,
        'green_zone': green_zone,
    }
    return render(request, 'reports/expiry_alerts.html', context)

def daily_sales(request):
    today = timezone.now().date()
    date_str = request.GET.get('date')
    if date_str:
        today = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        
    sales = SalesInvoice.objects.filter(date__date=today).order_by('-date')
    returns = SalesReturn.objects.filter(date__date=today).select_related('invoice').order_by('-date')
    
    summary = sales.aggregate(
        total_sales=Sum('grand_total'),
        total_discount=Sum('discount_amount'),
        total_tax=Sum('tax_amount')
    )
    returns_total = returns.aggregate(total_returns=Sum('refund_amount'))['total_returns'] or 0
    net_sales = (summary['total_sales'] or 0) - returns_total
    
    context = {
        'sales': sales,
        'summary': summary,
        'returns': returns,
        'returns_total': returns_total,
        'net_sales': net_sales,
        'date': today,
    }
    return render(request, 'reports/daily_sales_report.html', context)
