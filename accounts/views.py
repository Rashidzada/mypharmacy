from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone
from .models import Expense
from sales.models import SalesInvoice, SalesReturn
from purchases.models import PurchaseInvoice, PurchaseItem
from django import forms
from django.contrib import messages
from datetime import date as date_type
from datetime import datetime as datetime_type

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'amount', 'note']
        widgets = {
             'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
             'category': forms.TextInput(attrs={'class': 'form-control'}),
             'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
             'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

def cash_summary(request):
    today = timezone.localdate()

    # 1. Cash In (Sales - Assuming all Sales are Cash for "Cash In" simplicity, or filter by payment_mode='CASH')
    # User said "Sales vs purchase cash flow".
    sales_total = SalesInvoice.objects.filter(date__date=today).aggregate(total=Sum('grand_total'))['total'] or 0

    # 2. Cash Out (Purchases)
    purchases_total = PurchaseItem.objects.filter(invoice__date=today).aggregate(total=Sum('total_amount'))['total'] or 0

    # 3. Expenses
    expenses_total = Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0

    # 4. Returns (Refunds)
    returns_total = SalesReturn.objects.filter(date__date=today).aggregate(total=Sum('refund_amount'))['total'] or 0
    
    net_cash = sales_total - (purchases_total + expenses_total + returns_total)

    # Expense Form handling
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense recorded.')
            return redirect('cash_summary')
    else:
        form = ExpenseForm(initial={'date': today})

    recent_expenses = Expense.objects.filter(date=today).order_by('-id')
    today_purchases = (
        PurchaseInvoice.objects.filter(date=today)
        .select_related('supplier')
        .annotate(total_amount=Sum('items__total_amount'))
        .order_by('-id')
    )

    monthly_map = {}
    daily_map = {}

    def normalize_day(value):
        if not value:
            return None
        if isinstance(value, datetime_type):
            return value.date()
        if isinstance(value, date_type):
            return value
        if isinstance(value, str):
            parsed = parse_datetime(value) or parse_date(value)
            if not parsed:
                return None
            if isinstance(parsed, datetime_type):
                return parsed.date()
            return parsed
        return None

    def ensure_month(month_key):
        if month_key not in monthly_map:
            monthly_map[month_key] = {
                'month': month_key,
                'sales_total': 0,
                'purchases_total': 0,
                'expenses_total': 0,
                'returns_total': 0,
                'net_total': 0,
                'daily_records': [],
            }
        return monthly_map[month_key]

    def ensure_day(day_key):
        if day_key not in daily_map:
            daily_map[day_key] = {
                'day': day_key,
                'sales_total': 0,
                'purchases_total': 0,
                'expenses_total': 0,
                'returns_total': 0,
                'net_total': 0,
            }
        return daily_map[day_key]

    for row in SalesInvoice.objects.values('date', 'grand_total'):
        day_key = normalize_day(row['date'])
        if not day_key:
            continue
        amount = row['grand_total'] or 0
        ensure_day(day_key)['sales_total'] += amount
        ensure_month(day_key.replace(day=1))['sales_total'] += amount

    for row in PurchaseItem.objects.values('invoice__date', 'total_amount'):
        day_key = normalize_day(row['invoice__date'])
        if not day_key:
            continue
        amount = row['total_amount'] or 0
        ensure_day(day_key)['purchases_total'] += amount
        ensure_month(day_key.replace(day=1))['purchases_total'] += amount

    for row in Expense.objects.values('date', 'amount'):
        day_key = normalize_day(row['date'])
        if not day_key:
            continue
        amount = row['amount'] or 0
        ensure_day(day_key)['expenses_total'] += amount
        ensure_month(day_key.replace(day=1))['expenses_total'] += amount

    for row in SalesReturn.objects.values('date', 'refund_amount'):
        day_key = normalize_day(row['date'])
        if not day_key:
            continue
        amount = row['refund_amount'] or 0
        ensure_day(day_key)['returns_total'] += amount
        ensure_month(day_key.replace(day=1))['returns_total'] += amount

    for day_key, data in daily_map.items():
        data['net_total'] = data['sales_total'] - (
            data['purchases_total'] + data['expenses_total'] + data['returns_total']
        )
        ensure_month(day_key.replace(day=1))['daily_records'].append(data)

    monthly_summaries = sorted(monthly_map.values(), key=lambda item: item['month'], reverse=True)
    for item in monthly_summaries:
        item['net_total'] = item['sales_total'] - (
            item['purchases_total'] + item['expenses_total'] + item['returns_total']
        )
        item['daily_records'] = sorted(item['daily_records'], key=lambda record: record['day'], reverse=True)

    context = {
        'sales_total': sales_total,
        'purchases_total': purchases_total,
        'expenses_total': expenses_total,
        'returns_total': returns_total,
        'net_cash': net_cash,
        'form': form,
        'recent_expenses': recent_expenses,
        'today_purchases': today_purchases,
        'monthly_summaries': monthly_summaries,
        'today': today,
    }
    return render(request, 'accounts/cash_summary.html', context)
