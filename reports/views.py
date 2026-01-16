from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from sales.models import SalesInvoice, SalesReturn
from .utils.expiry_alerts import get_expiry_alert_querysets

def expiry_alerts(request):
    zones = get_expiry_alert_querysets()
    
    context = {
        'expired': zones['expired'],
        'red_zone': zones['critical'],
        'yellow_zone': zones['medium'],
        'green_zone': zones['low'],
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
