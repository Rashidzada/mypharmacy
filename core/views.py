from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from sales.models import SalesInvoice
from inventory.models import Product
from reports.utils.expiry_alerts import get_expiry_alert_counts

def dashboard(request):
    today = timezone.now().date()
    
    # 1. Today's Sales
    todays_sales = SalesInvoice.objects.filter(date__date=today).aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    
    # 2. Low Stock (e.g., total quantity < 10)
    # This is complex in aggregation, so doing Python side for simplicity in MVP
    products = Product.objects.all().prefetch_related('batches')
    low_stock_count = 0
    for p in products:
        stock = sum(b.quantity for b in p.batches.all())
        if stock < 10: # Threshold
            low_stock_count += 1
            
    expiry_counts = get_expiry_alert_counts(today=today)
    expired_count = expiry_counts["expired"]
    
    # 4. Total Products
    total_products = Product.objects.count()
    
    # Recent Sales
    recent_sales = SalesInvoice.objects.order_by('-date')[:5]

    context = {
        'todays_sales': todays_sales,
        'low_stock': low_stock_count,
        'expired': expired_count,
        'total_products': total_products,
        'recent_sales': recent_sales,
        'expiry_counts': expiry_counts,
        'show_expiry_widget': request.user.is_authenticated
        and (request.user.is_staff or request.user.has_perm('reports.view_reports')),
    }
    return render(request, 'core/dashboard.html', context)



# This is a test Data to the Pharmacy DB not for real useage just a randum
# # core/views.py
# import random
# import string
# from datetime import timedelta, date
# from decimal import Decimal

# from django.conf import settings
# from django.db import transaction
# from django.http import JsonResponse
# from django.utils import timezone

# from accounts.models import Expense
# from inventory.models import Category, Brand, Product, Batch
# from purchases.models import Supplier, PurchaseInvoice, PurchaseItem
# from sales.models import Customer, SalesInvoice, SaleItem, SalesReturn, SalesReturnItem


# # ---------- helpers ----------
# def rstr(n=8):
#     return "".join(random.choices(string.ascii_letters + string.digits, k=n))

# def rdate(days_back=365):
#     return date.today() - timedelta(days=random.randint(0, days_back))

# def rdec(a=10, b=5000):
#     return Decimal(str(round(random.uniform(a, b), 2)))

# def rint(a=1, b=100):
#     return random.randint(a, b)


# def seed_data(request):
#     """
#     URL:
#     /seed_data/?n=5000&reset=1&key=dev
#     """
#     if not settings.DEBUG:
#         return JsonResponse({"error": "DEBUG must be True"}, status=403)

#     if request.GET.get("key") != "dev":
#         return JsonResponse({"error": "Invalid key"}, status=403)

#     n = int(request.GET.get("n", 5000))
#     reset = request.GET.get("reset") == "1"

#     with transaction.atomic():

#         # -------- RESET (FK-safe order) --------
#         if reset:
#             SalesReturnItem.objects.all().delete()
#             SalesReturn.objects.all().delete()
#             SaleItem.objects.all().delete()
#             SalesInvoice.objects.all().delete()

#             PurchaseItem.objects.all().delete()
#             PurchaseInvoice.objects.all().delete()

#             Batch.objects.all().delete()
#             Product.objects.all().delete()
#             Brand.objects.all().delete()
#             Category.objects.all().delete()

#             Supplier.objects.all().delete()
#             Customer.objects.all().delete()
#             Expense.objects.all().delete()

#         # -------- CATEGORY --------
#         Category.objects.bulk_create([Category(name=f"Category {i+1}") for i in range(n)])
#         categories = list(Category.objects.all())

#         # -------- BRAND --------
#         Brand.objects.bulk_create([Brand(name=f"Brand {i+1}") for i in range(n)])
#         brands = list(Brand.objects.all())

#         # -------- PRODUCT (correct fields) --------
#         Product.objects.bulk_create([
#             Product(
#                 brand=random.choice(brands),
#                 name=f"Generic {i+1}",
#                 category=random.choice(categories),
#                 company=f"Company {rstr(4)}",
#                 description="Seed test product",
#                 tax_percentage=rdec(0, 17),   # DecimalField
#             )
#             for i in range(n)
#         ])
#         products = list(Product.objects.all())

#         # -------- BATCH (correct fields) --------
#         Batch.objects.bulk_create([
#             Batch(
#                 product=random.choice(products),
#                 batch_number=f"BATCH-{i+1:06d}",
#                 expiry_date=rdate(365 * 3),
#                 purchase_price=rdec(30, 2000),
#                 sale_price=rdec(50, 3500),
#                 quantity=rint(10, 300),
#             )
#             for i in range(n)
#         ])
#         batches = list(Batch.objects.all())

#         # -------- SUPPLIER --------
#         Supplier.objects.bulk_create([
#             Supplier(
#                 name=f"Supplier {i+1}",
#                 contact_person=f"Person {rstr(5)}",
#                 phone=f"03{random.randint(100000000, 999999999)}",
#                 address="Test address",
#             )
#             for i in range(n)
#         ])
#         suppliers = list(Supplier.objects.all())

#         # -------- PURCHASE INVOICE (needs invoice_number) --------
#         PurchaseInvoice.objects.bulk_create([
#             PurchaseInvoice(
#                 supplier=random.choice(suppliers),
#                 invoice_number=f"SUP-{i+1:06d}-{rstr(4)}",
#                 date=rdate(365),
#                 sub_total=Decimal("0.00"),
#                 total_discount=Decimal("0.00"),
#                 total_tax=Decimal("0.00"),
#                 grand_total=Decimal("0.00"),
#                 note="Seed purchase invoice",
#             )
#             for i in range(n)
#         ])
#         purchase_invoices = list(PurchaseInvoice.objects.all())

#         # -------- PURCHASE ITEMS (custom save() exists -> use create/save) --------
#         # NOTE: This is slower but accurate and avoids bulk_create skipping save().
#         for i in range(n):
#             inv = random.choice(purchase_invoices)
#             prod = random.choice(products)
#             b = random.choice(batches)

#             qty = rint(1, 50)
#             unit_price = rdec(20, 2000)
#             sale_price = rdec(30, 3500)

#             PurchaseItem.objects.create(
#                 invoice=inv,
#                 product=prod,
#                 batch=b,
#                 batch_number=b.batch_number,
#                 expiry_date=b.expiry_date,
#                 quantity=qty,
#                 unit_price=unit_price,
#                 sale_price=sale_price,
#                 discount_percentage=Decimal("0.00"),
#                 discount_amount=Decimal("0.00"),
#                 tax_percentage=prod.tax_percentage or Decimal("0.00"),
#                 tax_amount=Decimal("0.00"),
#                 total_amount=Decimal("0.00"),
#             )

#         # -------- CUSTOMER --------
#         Customer.objects.bulk_create([
#             Customer(
#                 name=f"Customer {i+1}",
#                 phone=f"03{random.randint(100000000, 999999999)}",
#                 address="Customer address",
#             )
#             for i in range(n)
#         ])
#         customers = list(Customer.objects.all())

#         # -------- SALES INVOICE (invoice_number is unique; set manually to allow bulk_create) --------
#         now = timezone.now()
#         SalesInvoice.objects.bulk_create([
#             SalesInvoice(
#                 customer=random.choice(customers),
#                 date=now - timedelta(days=random.randint(0, 365)),
#                 invoice_number=f"INV-{i+1:06d}-{rstr(3)}",
#                 sub_total=Decimal("0.00"),
#                 discount_percentage=Decimal("0.00"),
#                 discount_amount=Decimal("0.00"),
#                 tax_amount=Decimal("0.00"),
#                 grand_total=Decimal("0.00"),
#                 amount_paid=Decimal("0.00"),
#                 change_amount=Decimal("0.00"),
#                 payment_mode=random.choice(["CASH", "CARD", "ONLINE"]),
#             )
#             for i in range(n)
#         ])
#         sales_invoices = list(SalesInvoice.objects.all())

#         # -------- SALE ITEMS (custom save() exists -> use create/save) --------
#         sale_items_created = []
#         for i in range(n):
#             inv = random.choice(sales_invoices)
#             prod = random.choice(products)
#             b = random.choice(batches)

#             qty = rint(1, 10)
#             unit_price = (b.sale_price or rdec(50, 3500))

#             item = SaleItem.objects.create(
#                 invoice=inv,
#                 product=prod,
#                 batch=b,
#                 item_name="",  # will auto-fill from product in save()
#                 quantity=qty,
#                 unit_price=unit_price,
#                 discount_percentage=Decimal("0.00"),
#                 discount_amount=Decimal("0.00"),
#                 tax_amount=Decimal("0.00"),
#                 total_amount=Decimal("0.00"),
#             )
#             sale_items_created.append(item)

#         # -------- SALES RETURN (smaller amount) --------
#         returns_count = max(1, n // 5)
#         SalesReturn.objects.bulk_create([
#             SalesReturn(
#                 invoice=random.choice(sales_invoices),
#                 date=timezone.now() - timedelta(days=random.randint(0, 365)),
#                 reason="Seed return",
#                 refund_amount=Decimal("0.00"),
#             )
#             for _ in range(returns_count)
#         ])
#         returns = list(SalesReturn.objects.all())

#         # -------- SALES RETURN ITEMS --------
#         for r in returns:
#             si = random.choice(sale_items_created)
#             qty = random.randint(1, min(2, si.quantity))
#             SalesReturnItem.objects.create(
#                 sales_return=r,
#                 sale_item=si,
#                 quantity=qty,
#                 unit_refund=Decimal(str(si.unit_price)),
#                 total_amount=Decimal(str(si.unit_price)) * Decimal(qty),
#             )

#         # -------- EXPENSE --------
#         Expense.objects.bulk_create([
#             Expense(
#                 date=rdate(365),
#                 category=random.choice(["Rent", "Bills", "Salary", "Maintenance", "Other"]),
#                 amount=rdec(100, 20000),
#                 note="Seed expense",
#             )
#             for i in range(n)
#         ])

#     return JsonResponse({"status": "success", "records_per_table": n, "reset": reset})
