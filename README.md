# Restaurant Management System

A web-based Restaurant Management System built with Django. Customers can browse the menu, place orders, and pay online in a test payment environment, while staff and admins manage orders, menu items, and view business statistics from dedicated dashboards.

---

## Technologies

- Python
- Django
- HTML
- CSS
- Bootstrap
- SQLite

---

## Main Features

- Role-based authentication (Admin, Staff, Customer)
- Restaurant home page with featured menu items and category browsing
- Menu management (add, edit, delete menu items) with image upload
- Menu search and category filtering
- Shopping cart with quantity management
- Checkout with delivery details (name, phone, address, notes)
- Razorpay Test Mode payment integration
- Order confirmation page
- Customer order history ("My Orders")
- Order cancellation (for orders still pending)
- Admin dashboard with order/revenue statistics
- Staff dashboard for day-to-day order handling
- Order status management (Pending, Confirmed, Preparing, Ready, Delivered, Cancelled)
- Sales/revenue statistics calculated from paid orders

---

## Project Structure

```
restaurant_project/
├── accounts/       # Custom User model, auth views, role-based dashboards
├── menu/           # Menu model, menu browsing/management views
├── orders/         # Cart, checkout, payment, and order management
├── templates/      # All HTML templates (Bootstrap-based)
├── media/          # Uploaded menu item images (created at runtime)
├── config/         # Django project settings and URL configuration
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/omayaseen/restaurant-management-system.git
cd restaurant-management-system
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

A fresh database starts completely empty — no users and no menu items. See "Creating an Admin Account" and "Menu Items & Images" below for how to get the app into a usable state.

### 5. Run the development server

```bash
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser.

---

## Creating an Admin Account

This project uses a **custom User model** with a `role` field (`admin`, `staff`, or `customer`). Django's standard `createsuperuser` command does not know about this field, so a newly created superuser defaults to `role = customer` and will not see the application's admin dashboard.

To get a working admin account:

1. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
2. Start the server and log into Django's built-in admin site at `http://127.0.0.1:8000/admin/` using that superuser's credentials.
3. Under **Accounts → Users**, open the user you just created and change its **role** field to `admin`, then save.
4. Log into the application itself (not `/admin/`) at `http://127.0.0.1:8000/login/` with the same credentials. You will now be redirected to the admin dashboard.

Staff accounts can be created the same way: register normally through the app's registration page (which creates a `customer` by default), then change that user's `role` to `staff` from `/admin/`.

---

## Menu Items & Images

A fresh database has no menu items. Once you have an admin account (see above), log in and use the **Add Menu** page (linked from the admin dashboard and navbar) to create menu items, including uploading an image for each one.

Uploaded images are stored under the `media/` folder and served via `MEDIA_URL`/`MEDIA_ROOT` while `DEBUG = True`. This is a development-only setup — a production deployment would need a separate media-serving configuration (e.g. a cloud storage backend or a web server rule), which is outside the scope of this project.

---

## Razorpay Test Mode (Payment Integration)

Checkout uses [Razorpay](https://razorpay.com/) in **Test Mode** — no real payments are ever processed, and no real money moves. To enable the payment step locally:

1. Create a free Razorpay account and switch the dashboard to **Test Mode**.
2. Go to **Settings → API Keys** and generate a Test Mode Key Id and Key Secret.
3. Supply them to the app as environment variables (never commit these to source control):
   ```bash
   export RAZORPAY_KEY_ID="your_test_key_id"
   export RAZORPAY_KEY_SECRET="your_test_key_secret"
   ```
   (On Windows: `set RAZORPAY_KEY_ID=your_test_key_id`, etc.)
4. Restart the development server so the environment variables are picked up.

If these environment variables are not set, the payment page will show a "Payment gateway is not configured" message instead of failing — the rest of the application works normally without them.

This project is configured for Razorpay **Test Mode only**. Using it with real payments would require production API credentials and additional configuration, which this project is not set up to do out of the box.

---

## Quick Reference

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Author

**Mukhtar Ahmed Yaseen O**

GitHub: https://github.com/omayaseen
