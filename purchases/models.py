from django.db import models
from inventory.models import Product, Batch
from django.utils import timezone
from decimal import Decimal

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class PurchaseInvoice(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True, help_text="Supplier's Invoice Number")
    date = models.DateField(default=timezone.now)
    
    # These fields are usually aggregates, but good to store for integrity
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"INV-{self.invoice_number} ({self.supplier.name})"

class PurchaseItem(models.Model):
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    # We store batch link. If this is a new batch, it gets created.
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_items')
    
    # Input fields ensuring we can create a batch
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Purchase Price per unit")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Suggested Sale Price")
    
    # Item-level Discount (Percentage or Amount)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Tax
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Basic calculation (can be overridden by JS frontend, but good for safety)
        # Gross = qty * unit_price
        # Disc = Gross * (disc_perc / 100) OR fixed amount
        # Tax = (Gross - Disc) * (tax_perc / 100)
        # Total = Gross - Disc + Tax
        
        # Ensure all inputs are Decimal
        qty = Decimal(self.quantity or 0)
        u_price = Decimal(self.unit_price or 0)
        d_perc = Decimal(self.discount_percentage or 0)
        d_amt = Decimal(self.discount_amount or 0)
        t_perc = Decimal(self.tax_percentage or 0)
        t_amt = Decimal(self.tax_amount or 0)
        
        gross = qty * u_price
        
        # Priority: if amount is set manually, use it. Else calc from percent.
        if d_amt == 0 and d_perc > 0:
            d_amt = gross * (d_perc / Decimal(100))
        
        # Write back calculated/casted to model
        self.discount_percentage = d_perc
        self.discount_amount = d_amt
            
        taxable_amount = gross - d_amt
        
        if t_amt == 0 and t_perc > 0:
            t_amt = taxable_amount * (t_perc / Decimal(100))
        
        # Write back calculated/casted to model
        self.tax_percentage = t_perc
        self.tax_amount = t_amt
            
        self.total_amount = taxable_amount + t_amt
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} qty"
