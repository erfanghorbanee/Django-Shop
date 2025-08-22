# Django Shop

<p align="center">
  <img src="Django-Shop/static/shared/images/icon.png" alt="Logo" width="200"/>
</p>

Django Shop is a modern, responsive e-commerce platform built with [Django](https://www.djangoproject.com/) and [Bootstrap](https://getbootstrap.com/). It allows users to browse, search for products, manage shopping cart, and make purchases.

## Table of Contents

- [Django Shop](#django-shop)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Demo](#demo)
  - [Installation](#installation)
  - [Running the Project](#running-the-project)
  - [Seeding / Creating Products (management command)](#seeding--creating-products-management-command)
  - [Stripe Payments: Local Testing](#stripe-payments-local-testing)
  - [Google OAuth Setup (Login with Google)](#google-oauth-setup-login-with-google)
    - [1. Register your app with Google](#1-register-your-app-with-google)
    - [2. Configure Django settings](#2-configure-django-settings)
  - [To-Do List](#to-do-list)
  - [License](#license)

## Features

- Modern, responsive UI with light/dark mode switcher (Bootstrap 5)
- User authentication, registration, account management, and social login (via [`Django Allauth`](https://docs.allauth.org/))
- Phone number validation (via [`Django-PhoneNumberField`](https://django-phonenumber-field.readthedocs.io/))
- Secure file uploads with validation
- Products:
  - Listing, detail pages, and search
  - Product ratings and reviews
  - Discounts and promotions
  - Robust inventory management: stock is atomically decremented on successful payment confirmation
- Shopping cart:
  - Persistent carts for guests (session) and authenticated users; automatic merge on login
  - Per-item quantity limits (`CART_MAX_ITEM_QTY` in `settings.py`)
  - Cart icon in Navbar shows total items (via context processors)
- Order management:
  - Decoupled order and payment status for accurate tracking
  - Payment via Stripe (powered by [`django-payments`](https://github.com/mirumee/django-payments))
  - Orders are only marked as paid and processed after Stripe/Admin confirms payment
  - Automatic cancellation and error messaging if stock is insufficient at payment time
- User wishlist functionality
- Customer support and contact page
- Career application page
- Advanced address management:
  - Multiple addresses per user with exactly one primary (DB-enforced)
  - First address auto-set as primary
  - Safe primary switching (atomic demotion of previous primary)
  - Cannot delete the only remaining address
  - Automatic promotion of a new primary after deleting the current one
- Use `pytest`, `pytest-django`, and `model-bakery` for fast, expressive tests

## Demo

![Demo Gif](Gallary/demo.gif)

Below are screenshots demonstrating some of the key pages and features (image files are in `Gallary/`):

- **Homepage** — Carousel and featured discounts

  ![Homepage screenshot](Gallary/home.png)

- **Product detail**

  ![Product detail screenshot](Gallary/product-detail.png)

- **Cart**

  ![Cart screenshot](Gallary/cart.png)

- **Sign in** — Authentication page with Google option

  ![Sign in screenshot](Gallary/signin.png)

## Installation

0. (Recommended) Use a virtual environment:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

1. Clone the repository:

    ```bash
    git clone https://github.com/erfanghorbanee/Django-Shop.git
    cd Django-Shop
    ```

2. Install the Python dependencies:

    ```bash
    pip install -r requirements/local.txt
    ```

## Running the Project

1. Apply migrations:

    ```bash
    cd Django-Shop
    python manage.py makemigrations
    python manage.py migrate
    ```

2. Create a superuser:

    ```bash
    python manage.py createsuperuser
    ```

3. Run the development server:

    ```bash
    python manage.py runserver
    ```

4. Open your browser and go to `http://127.0.0.1:8000`.

## Seeding / Creating Products (management command)

You can create sample products, categories, and product images using the built-in management command `seed_products`.

Example usage (from the project root):

```bash
python manage.py seed_products
```

Options:

- `--products` N (default: `50`) — total number of products to create
- `--images` M (default: `2`) — number of images to attach per product

Notes:

- The command removes existing `Category`, `Product`, and `ProductImage` records before seeding, so use with care.
- Product images are fetched from [picsum.photos](https://picsum.photos) at runtime; an internet connection is required and the `requests` package must be available.

## Stripe Payments: Local Testing

You can test the payment flow locally with Stripe (using `django-payments` + Stripe Provider V3).

Prerequisites

- A Stripe account (free).
- Stripe CLI installed.

Install Stripe CLI (macOS):

```bash
brew install stripe/stripe-cli/stripe
```

Login to Stripe from the CLI:

```bash
stripe login
```

Export your Stripe API key (test key) so the app can create sessions/intents:

```bash
export STRIPE_API_KEY="sk_test_..."
```

Forward webhooks to Django (required):

```bash
stripe listen --forward-to http://127.0.0.1:8000/payments/stripe/webhook/
```

This prints a signing secret like `whsec_...`.

- Easiest path (no signature verification in dev): keep `secure_endpoint: False` in `PAYMENT_VARIANTS` (in `config/settings.py`) and just keep the CLI running to forward events.
- With signature verification (optional, stricter):
  1) Add the secret to your environment: `export STRIPE_ENDPOINT_SECRET="whsec_..."`
  2) In `config/settings.py`, set the Stripe variant with `"endpoint_secret": os.getenv("STRIPE_ENDPOINT_SECRET")` and `"secure_endpoint": True`.

Now, run the app and go through checkout.

Test card for a successful payment:

- Number: `4242 4242 4242 4242`
- Expiry: any future date (e.g., 12/34)
- CVC: any 3 digits (e.g., 123)

Official references:

- [Stripe CLI docs](https://stripe.com/docs/stripe-cli)
- [Stripe CLI webhooks](https://stripe.com/docs/stripe-cli/webhooks)
- [Stripe test cards](https://stripe.com/docs/testing?testing-method=card-numbers#cards)

## Google OAuth Setup (Login with Google)

To enable users to log in or register using their Google account, follow these steps:

### 1. Register your app with Google

- Go to the [Google Cloud Console](https://console.developers.google.com/).
- Create a new project (or select an existing one).
- Navigate to **APIs & Services > Credentials**.
- Click **Create Credentials > OAuth client ID**.
- Set the application type to **Web application**.
- Add the following to **Authorized redirect URIs**:
  - `http://127.0.0.1:8000/accounts/google/login/callback/`
  - This is for when we run the app locally.
- Save and copy the **Client ID** and **Client Secret**.

### 2. Configure Django settings

In `Django-Shop/config/settings.py`, update the `SOCIALACCOUNT_PROVIDERS` section:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID',
            'secret': 'YOUR_GOOGLE_CLIENT_SECRET',
            'key': ''
        }
    }
}
```

## To-Do List

- **Async & Performance**
  - Add async support for views and background tasks
  - Optimize database queries and overall speed
  - Implement caching for products, categories, and frequently accessed data
  - Move DB to PostgreSQL

- **Admin & Dashboard**
  - Customize admin dashboard for management

- **Product Discovery & Media**
  - Add product filters (category, price, rating, etc.)
  - Process and optimize images (static and media)

- **Payments & Orders**
  - Add support for additional payment providers (PayPal, Apple Pay, etc.)
  - Improve payment error handling and user feedback

- **User Experience & Security**
  - Improve security (2FA, rate limiting, etc.)
  - Add user notifications (email, in-app) for order/payment status
  - Support multiple languages (i18n: Italian, German, ...)
  - Optimize for SEO and accessibility
  - Separate settings for dev and prod
  - Follow cookiecutter practices
  - Dockerize the project

- **Testing & Quality**
  - Increase test coverage for all core features
  - Stress-test server and database under heavy load with concurrent requests

## License

This project is licensed under the GNU General Public License v3.0. See the full text in the [LICENSE file](LICENSE).
