from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    # According to requirements: Brand Name, Generic Name, Company, Category
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200, help_text="Generic Name")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    company = models.CharField(max_length=100, blank=True, help_text="Company Name")
    description = models.TextField(blank=True)
    
    # Tax rules: Apply only if product has tax.
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Tax percentage (0 to 100)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} ({self.name})"

class Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    
    # Prices
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Leave empty to enter manually during sale")
    
    # Stock
    quantity = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product} - {self.batch_number}"
