# Django Shop

<p align="center">
  <img src="Django-Shop/static/shared/images/icon.png" alt="Logo" width="200"/>
</p>

Django Shop is a modern, responsive e-commerce platform built with [Django](https://www.djangoproject.com/) and [Bootstrap](https://getbootstrap.com/). It allows users to browse, search for products, manage shopping carts, and make purchases. The platform uses [Django Allauth](https://docs.allauth.org/) for authentication and supports social login.

## Table of Contents
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [To-Do List](#to-do-list)
- [License](#license)

## Features
- User Authentication, Registration, Account management, and Social login (via [Django Allauth](https://docs.allauth.org/))
- Phone number validation (via [Django-PhoneNumberField](https://django-phonenumber-field.readthedocs.io/))
- Responsive design using [Bootstrap](https://getbootstrap.com/)
- Clean UI with light/dark mode switcher

## Demo
*Demo GIF goes here*

## Installation

### Steps
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

## To-Do List

- [ ] Add payment integration
- [ ] Implement cart
- [ ] Improve overall speed
- [ ] Customize dashboard for admins
- [ ] process and optimize pictures(static and media)
- [ ] Optimize for SEO
- [ ] Optimize caching
- [ ] Improve security (2fa, ...)
- [ ] Support other languages (French, German, ...)

## License

This project is licensed under the GNU General Public License v3.0. You can read more about it [here](LICENSE).
