from django.db import models
from django.utils import timezone
from inventory.models import Product, Batch

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SalesInvoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Financials
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Bill-level Discount
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    change_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    PAYMENT_MODES = (
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('ONLINE', 'Online'),
    )
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES, default='CASH')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Auto-increment invoice number logic
            last_invoice = SalesInvoice.objects.all().order_by('id').last()
            if last_invoice:
                last_id = last_invoice.id
            else:
                last_id = 0
            self.invoice_number = f"INV-{last_id + 1:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number}"

class SaleItem(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, null=True, blank=True)
    
    # Snapshot of name, because product link might be null for manual items
    item_name = models.CharField(max_length=200, blank=True, help_text="Product Name or Manual Item Name")
    
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling Price at time of sale")
    
    # Item-level Discount
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    def save(self, *args, **kwargs):
        # Auto-fill item_name from product if not set
        if not self.item_name and self.product:
            self.item_name = self.product.name
            
        # Ensure Decimal
        from decimal import Decimal
        qty = Decimal(self.quantity)
        u_price = Decimal(self.unit_price)
        d_perc = Decimal(self.discount_percentage)
        d_amt = Decimal(self.discount_amount)
        t_amt = Decimal(self.tax_amount or 0)
        
        gross = qty * u_price
        
        # Priority: if amount is set manually, use it. Else calc from percent.
        if d_amt == 0 and d_perc > 0:
            d_amt = gross * (d_perc / Decimal(100))
        
        self.discount_amount = d_amt # save back
        
        taxable_amount = gross - d_amt
        self.tax_amount = t_amt
        self.total_amount = taxable_amount + t_amt
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.item_name or (self.product.name if self.product else "Item")
        return f"{name} ({self.quantity})"
