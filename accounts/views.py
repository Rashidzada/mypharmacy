from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone
from .models import Expense
from sales.models import SalesInvoice, SalesReturn
from purchases.models import PurchaseInvoice, PurchaseItem
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date as date_type
from datetime import datetime as datetime_type
from .utils.excel_export import (
    build_daily_workbook,
    build_monthly_workbook,
    export_workbook_response,
)

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


def _build_monthly_summaries():
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

    return monthly_summaries


def _parse_month_param(value):
    if not value:
        return None
    try:
        return datetime_type.strptime(value, "%Y-%m").date()
    except ValueError:
        return None


def _parse_year_param(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _is_truthy(value):
    return str(value).lower() in {"1", "true", "yes", "y", "on"}


@login_required
def export_daily_records(request):
    month_param = request.GET.get("month")
    selected_month = _parse_month_param(month_param) or timezone.localdate().replace(day=1)
    monthly_summaries = _build_monthly_summaries()
    month_record = next(
        (record for record in monthly_summaries if record["month"] == selected_month),
        None,
    )
    daily_records = month_record["daily_records"] if month_record else []
    workbook = build_daily_workbook(daily_records)
    filename = f"daily_records_{selected_month:%Y-%m}.xlsx"
    return export_workbook_response(workbook, filename)


@login_required
def export_monthly_records(request):
    month_param = request.GET.get("month")
    selected_month = _parse_month_param(month_param) or timezone.localdate().replace(day=1)
    monthly_summaries = _build_monthly_summaries()
    month_record = next(
        (record for record in monthly_summaries if record["month"] == selected_month),
        None,
    )
    monthly_records = [month_record] if month_record else []
    daily_records = month_record["daily_records"] if month_record else []
    workbook = build_monthly_workbook(monthly_records, daily_records)
    filename = f"monthly_records_{selected_month:%Y-%m}.xlsx"
    return export_workbook_response(workbook, filename)


@login_required
def export_yearly_summary(request):
    year_param = request.GET.get("year")
    selected_year = _parse_year_param(year_param) or timezone.localdate().year
    monthly_summaries = _build_monthly_summaries()
    year_records = [record for record in monthly_summaries if record["month"].year == selected_year]
    include_daily = _is_truthy(request.GET.get("include_daily"))
    daily_records = None
    if include_daily:
        daily_records = sorted(
            (record for month in year_records for record in month["daily_records"]),
            key=lambda item: item["day"],
            reverse=True,
        )
    workbook = build_monthly_workbook(year_records, daily_records)
    filename = f"yearly_summary_{selected_year}.xlsx"
    return export_workbook_response(workbook, filename)
