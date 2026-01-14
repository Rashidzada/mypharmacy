import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings')
django.setup()

from purchases.models import PurchaseInvoice, PurchaseItem, Supplier
from inventory.models import Product, Brand, Category, Batch
from django.utils import timezone

def verify_fix():
    print("Verifying PurchaseItem save() logic...")
    
    # Setup dummy data
    try:
        supplier, _ = Supplier.objects.get_or_create(name="Test Supplier")
        category, _ = Category.objects.get_or_create(name="Test Cat")
        brand, _ = Brand.objects.get_or_create(name="Test Brand")
        product, _ = Product.objects.get_or_create(
            name="Test Prod", 
            defaults={'brand': brand, 'category': category, 'tax_percentage': 0}
        )
        invoice = PurchaseInvoice.objects.create(supplier=supplier, invoice_number="TEST-001")
        
        # Test Case: inputs might be floats or mix
        # Model fields default to 0.00 which is float in python code if not casted by Django fetch
        # But here we simulate the worst case: direct assignment of floats
        item = PurchaseItem(
            invoice=invoice,
            product=product,
            batch_number="B001",
            expiry_date=timezone.now().date(),
            quantity=10,
            unit_price=10.5, # Float
            discount_percentage=5.0, # Float
            tax_percentage=2.5, # Float
            discount_amount=0.0, # Float
            tax_amount=0.0 # Float
        )
        
        print("Attempting to save item with float inputs...")
        item.save()
        
        print("Success! Item saved.")
        print(f"Total Amount: {item.total_amount} (Type: {type(item.total_amount)})")
        
        # Cleanup
        invoice.delete()
        product.delete()
        print("Cleanup done.")
        
    except Exception as e:
        print("\n!!! FAILED !!!")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_fix()
