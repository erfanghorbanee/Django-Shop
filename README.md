# Django Shop

<p align="center">
  <img src="Django-Shop/static/shared/images/icon.png" alt="Logo" width="200"/>
</p>

Django Shop is a modern, responsive e-commerce platform built with [Django](https://www.djangoproject.com/) and [Bootstrap](https://getbootstrap.com/). It allows users to browse, search for products, manage shopping carts, and make purchases. The platform uses [Django Allauth](https://docs.allauth.org/) for authentication and supports social login.

## Table of Contents

- [Django Shop](#django-shop)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Demo](#demo)
  - [Installation](#installation)
  - [Running the Project](#running-the-project)
  - [Google OAuth Setup (Login with Google)](#google-oauth-setup-login-with-google)
    - [1. Register your app with Google](#1-register-your-app-with-google)
    - [2. Configure Django settings](#2-configure-django-settings)
  - [To-Do List](#to-do-list)
  - [License](#license)

## Features

- User Authentication, Registration, Account management, and Social login (via [`Django Allauth`](https://docs.allauth.org/))
- Phone number validation (via [`Django-PhoneNumberField`](https://django-phonenumber-field.readthedocs.io/))
- Validating uploaded Files
- Responsive design using [`Bootstrap`](https://getbootstrap.com/)
- Clean UI with light/dark mode switcher
- Products listing and details
  - Product Rating and Reviews
  - Discounts/Promotions
- Order management
- User wishlist functionality
- Customer support page
- Career application page
- Advanced address management
  - Multiple addresses per user with exactly one primary (DB-enforced partial unique constraint)
  - First address auto-set as primary
  - Safe primary switching (atomic demotion of previous primary)
  - Cannot delete the only remaining address
  - Automatic promotion of a new primary (most recent address) after deleting the current one
- Shopping Cart:
  - Persistent carts for guests (session) and authenticated users; automatic merge on login
  - Limit per item (`CART_MAX_ITEM_QTY` in `settings.py`)
  - Cart icon in Navbar shows the total number of added items via `context processors`.
- Use `pytest` + `pytest-django` and `model-bakery` for fast, expressive tests.

## Demo

*Demo GIF goes here*

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

- [ ] Add Async
- [ ] Improve overall speed
- [ ] Customize dashboard for admins
- [ ] process and optimize pictures(static and media)
- [ ] Optimize for SEO
- [ ] Optimize caching
- [ ] Improve security (2fa, ...)
- [ ] Test
  - [ ] Add tests for core functionalities
  - [ ] stress-test server and database under heavy load with concurrent requests
- [ ] Support other languages (French, German, ...)

## License

This project is licensed under the GNU General Public License v3.0. See the full text in the [LICENSE file](LICENSE).
