from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils import timezone
from .models import Expense
from sales.models import SalesInvoice
from purchases.models import PurchaseInvoice
from django import forms
from django.contrib import messages

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
    today = timezone.now().date()
    
    # 1. Cash In (Sales - Assuming all Sales are Cash for "Cash In" simplicity, or filter by payment_mode='CASH')
    # User said "Sales vs purchase cash flow".
    sales_total = SalesInvoice.objects.filter(date__date=today).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # 2. Cash Out (Purchases)
    purchases_total = PurchaseInvoice.objects.filter(date=today).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # 3. Expenses
    expenses_total = Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0
    
    net_cash = sales_total - (purchases_total + expenses_total)
    
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

    context = {
        'sales_total': sales_total,
        'purchases_total': purchases_total,
        'expenses_total': expenses_total,
        'net_cash': net_cash,
        'form': form,
        'recent_expenses': recent_expenses,
        'today': today
    }
    return render(request, 'accounts/cash_summary.html', context)
