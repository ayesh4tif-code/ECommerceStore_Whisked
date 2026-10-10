# Whisked Django backend

This project serves the existing `index.html` storefront and provides a small JSON API backed by SQLite.

## Run locally

From the repository root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python backend\manage.py migrate
python backend\manage.py seed_products
python backend\manage.py runserver
```

Open `http://127.0.0.1:8000/`. Django serves the storefront and API from the same origin.

## API

- `GET /api/products/` — active catalog.
- `POST /api/auth/register/` — create an account and sign in.
- `POST /api/auth/login/` — sign in with email and password.
- `POST /api/auth/logout/` — end the current session.
- `GET /api/auth/me/` — current session account.
- `POST /api/orders/` — place a delivery or pickup order. Product prices and cake-size surcharges are calculated by the server.
- `GET /api/orders/mine/` — list orders belonging to the signed-in account with current fulfillment status.

JSON POST requests require Django's CSRF cookie/header. The storefront handles this automatically. Use Django admin at `/admin/` to manage products and view orders; create an admin account with `python backend\manage.py createsuperuser`.

Payment processing is not configured; orders are recorded as received and the bakery follows up about payment.
Order statuses can be updated by staff in Django admin (`Received`, `Baking`, `Ready`, or `Completed`). Orders placed while signed in are attached to that account; guest orders remain anonymous and are not exposed in account tracking.

For deployment, set a unique `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, configure `DJANGO_ALLOWED_HOSTS`, and serve the site over HTTPS.
