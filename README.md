# ShopSphere — Django E-commerce

A Django-based e-commerce application with a customer storefront and a custom staff-only administration dashboard.

## Admin dashboard

Open `/dashboard/` after signing in with a Django staff/superuser account.

- Dashboard overview: product, category, brand and order totals, paid revenue, pending orders, recent orders and low-stock alerts.
- Products: create, view, search, edit and delete products, including image, SKU, category, brand, pricing, discounts, stock and visibility.
- Categories: create, list, edit and delete categories, including image and active status.
- Brands: create, list, edit and delete brands, including logo and active status.
- Coupons: create and delete coupons with percentage, minimum order, maximum discount, usage limit and validity period.
- Orders: search/filter all orders, view order items and customer/shipping information, and update order/payment statuses.

All custom dashboard views require `is_staff` or `is_superuser`; customer accounts cannot access them. The built-in Django `createsuperuser` command creates an administrator account.

## Technology

- Python / Django 5.2
- Django templates, HTML, CSS, Bootstrap 5 and JavaScript
- SQLite by default (database can be configured in `config/settings.py`)
- Pillow for image uploads

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations:

   ```bash
   python manage.py migrate
   ```

4. Create an admin user:

   ```bash
   python manage.py createsuperuser
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. Visit `http://127.0.0.1:8000/` for the storefront and `http://127.0.0.1:8000/dashboard/` for the admin dashboard.

## Static and media files

- Static source files: `static/`
- Collected static files: `staticfiles/` (`python manage.py collectstatic`)
- Uploaded media: `media/`

For production, set a secure `SECRET_KEY`, configure `ALLOWED_HOSTS`, set `DEBUG=False`, configure the production database, and serve collected static and uploaded media files through the hosting server or a suitable storage backend.

## Important

The dashboard uses the existing `ProductModel`, `CategoryModel`, `BrandModel`, `CouponModel`, and `OrderModel` models. It does not create duplicate catalog/order tables. Order status changes are validated against the model's declared choices.
