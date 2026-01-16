# Pharmacy WebApp (Django)

A Django-based pharmacy management web application covering inventory (products/batches/stock), purchases (supplier invoices/stock-in), sales/POS (stock-out with FIFO batches, invoice print, returns), expiry alerts, and cash-flow summary with Excel exports.

> Tech stack: Django 6.x, Python 3.x, SQLite (default) or PostgreSQL (optional), Bootstrap-based templates, openpyxl for Excel exports.

---

## Key Features

- **Dashboard**: Today's sales total, low-stock count, expiry alerts summary, total products, recent sales.
- **Inventory**: Products linked to **Brand** and **Category**, batch-wise stock, tax percentage per product.
- **Purchases (Stock In)**: Supplier management, purchase invoice entry, auto batch creation, totals (subtotal/discount/tax/grand total).
- **Sales / POS (Stock Out)**:
  - Product search API (shows price, stock, tax)
  - Create sale via API (supports manual items + inventory items)
  - FIFO batch selection by earliest expiry date
  - Invoice print view
- **Sales Returns**: Return items from an invoice, stock is restored to batch, refund amount tracked.
- **Reports**:
  - Expiry alerts by zones (expired, <=45 days, 46-90 days, 91-180 days)
  - Daily sales report with returns and net sales
- **Accounts / Cash Summary**:
  - Daily sales vs purchases vs expenses vs returns
  - Monthly grouping
  - Excel export (daily/month/year)

---

## Modules / Apps

- `core` - dashboard
- `inventory` - category/brand/product/batch/stock
- `purchases` - supplier + purchase invoices
- `sales` - POS, invoices, returns
- `reports` - expiry + daily sales
- `accounts` - expenses + cash summary + Excel export

---

## Quick Start (Local)

### 1) Create and activate virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not present, install at least:

```bash
pip install django openpyxl
```

### 3) Run migrations

```bash
python manage.py migrate
```

### 4) Create admin user

```bash
python manage.py createsuperuser
```

### 5) Run server

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

---

## Main URLs

- Dashboard: `/`
- Login: `/auth/login/`
- Admin: `/admin/`

### Inventory
- Products: `/inventory/products/`
- Add Product: `/inventory/products/add/`
- Edit Product: `/inventory/products/<id>/edit/`
- Add Stock (Batch): `/inventory/products/<id>/add-stock/`

### Purchases
- Suppliers: `/purchases/suppliers/`
- Add Supplier: `/purchases/suppliers/add/`
- New Purchase Invoice: `/purchases/new/`

### Sales
- POS: `/sales/pos/`
- Product Search API: `/sales/api/search/?q=panadol`
- Create Sale API: `/sales/api/create/` (POST JSON)
- Invoice Print: `/sales/invoice/<id>/print/`
- Invoice Return: `/sales/invoice/<id>/return/`

### Reports
- Expiry Alerts: `/reports/expiry-alerts/`
- Daily Sales: `/reports/daily-sales/?date=YYYY-MM-DD`

### Accounts
- Cash Summary: `/accounts/summary/`
- Export Daily Records: `/accounts/summary/export/daily/?month=YYYY-MM`
- Export Monthly Records: `/accounts/summary/export/month/?month=YYYY-MM`
- Export Yearly Summary: `/accounts/summary/export/year/?year=YYYY&include_daily=1`

---

## Sales API Payload Example

```json
{
  "customer_name": "Ali",
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
    },
    {
      "type": "manual",
      "name": "Service Charge",
      "quantity": 1,
      "price": 50
    }
  ]
}
```

---

## Notes / Production Checklist

- Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Move `SECRET_KEY` to environment variables.
- Use PostgreSQL in production (settings template is included).
- Add proper user roles/permissions (staff vs cashier vs manager).
- Add automated tests for purchase/sale/returns flows.

---

## License

This repository can be licensed per client agreement.
