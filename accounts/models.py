from django.db import models
from django.utils import timezone

class Expense(models.Model):
    date = models.DateField(default=timezone.now)
    category = models.CharField(max_length=100) # e.g., Rent, Bills
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.category} - {self.amount}"
