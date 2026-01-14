# MyPharmacy

MyPharmacy is a Django-based pharmacy management and POS system. It covers inventory, purchases, sales, reporting, and day-to-day cash tracking in one web app.

## Features
- Product catalog with brands, categories, and generic names
- Batch-level stock tracking with expiry dates and pricing
- Purchasing workflow with suppliers and automatic stock updates
- POS sales screen with search, FIFO batch handling, and manual items
- Discounts and tax calculations at item and invoice levels
- Customer capture (name/phone) and invoice printing
- Dashboard with today's sales, low stock, and expiry alerts
- Reports: expiry alerts and daily sales summary
- Cash summary with expenses logging

## Tech Stack
- Django (server-side MVC)
- SQLite (default dev database)
- Django templates with static assets in `static/`

## Apps
- `core`: dashboard landing page
- `inventory`: products, batches, stock
- `purchases`: suppliers and purchase invoices
- `sales`: POS, customers, invoices
- `reports`: expiry and daily sales reports
- `accounts`: cash summary and expenses

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Setup
1. Create and activate a virtual environment.
   - Windows:
     `python -m venv .venv`
     `.venv\Scripts\activate`
   - macOS/Linux:
     `python -m venv .venv`
     `source .venv/bin/activate`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run migrations:
   `python manage.py migrate`
4. Create an admin user:
   `python manage.py createsuperuser`
5. Start the server:
   `python manage.py runserver`
6. Open `http://127.0.0.1:8000/`

### Using the included database
A sample `db.sqlite3` is present. If you want a fresh database, delete `db.sqlite3` and re-run `migrate`.

## Key Routes
- `/` Dashboard
- `/inventory/products/` Product list
- `/inventory/products/add/` Add product
- `/inventory/products/<id>/add-stock/` Add batch stock
- `/purchases/suppliers/` Suppliers
- `/purchases/new/` New purchase invoice
- `/sales/pos/` POS
- `/sales/invoice/<id>/print/` Print invoice
- `/reports/expiry-alerts/` Expiry report
- `/reports/daily-sales/` Daily sales report
- `/accounts/summary/` Cash summary
- `/admin/` Django admin

## Sales API (POS)
- `GET /sales/api/search/?q=term` returns product suggestions with stock and pricing.
- `POST /sales/api/create/` creates a sale.

Example request:
```json
{
  "customer_name": "Ali Khan",
  "customer_phone": "03001234567",
  "payment_mode": "CASH",
  "discount_percentage": 0,
  "discount_amount": 0,
  "sub_total": 500,
  "tax_total": 0,
  "grand_total": 500,
  "amount_paid": 500,
  "change_amount": 0,
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 250,
      "discount_percentage": 0,
      "discount_amount": 0,
      "tax_amount": 0,
      "total": 500
    }
  ]
}
```

Manual item example:
```json
{ "type": "manual", "name": "Custom Item", "quantity": 1, "price": 100 }
```

## Running Tests
`python manage.py test`

## Configuration Notes
- Settings: `pharmacy_project/settings.py`
- Static files: `static/` (use `python manage.py collectstatic` for production)
- Media uploads: `media/`

## License
Not specified.
