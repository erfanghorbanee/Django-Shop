# Contributing to Django Shop

Thanks for your interest in contributing! This guide outlines a concise workflow and links to the README for environment setup and configuration details.

The project is licensed under GPL-3.0. By contributing, you agree your contributions will be licensed under the GPL-3.0 license.

## Ways to contribute

- Report bugs and propose enhancements
- Improve documentation (README, inline docs, comments)
- Add tests and fix failing tests
- Implement features aligned with the roadmap (see README To‑Do List or issues section)

**Before starting significant work, consider opening an issue to discuss your idea.**

## Quick start (see README for details)

- **Environment and installation**: see README “Installation”
- **Running the project**: see README “Running the Project”
- **Seeding sample data**: see README “Seeding / Creating Products (management command)”
- **Stripe local testing**: see README “Stripe Payments: Local Testing”
- **Google OAuth**: see README “Google OAuth Setup (Login with Google)”

## Coding standards

Python style: PEP 8, enforced by Ruff

Always run Ruff before committing: `ruff check .` and `ruff format`.

## Running tests

We use pytest, pytest-django, and model-bakery. From the project root: `pytest -q` (or run a specific test path when needed).

Guidelines:

- Add tests for any new feature or bug fix
- Prefer fast, isolated unit tests; use model-bakery for fixtures
- Keep database state explicit; avoid relying on implicit data

## Database changes and migrations

- Always create migrations for model changes and commit them with your PR
- Keep migrations clean, deterministic, and minimal
- One logical change per migration when possible

Common commands: `python manage.py makemigrations <app>` and `python manage.py migrate`.

If you rename or remove fields/models, verify data migrations and backward compatibility (when feasible) and document risks in the PR.

## Payments and OAuth (summary)

Never commit secrets or API keys; use environment variables. For setup and commands, see README sections “Stripe Payments: Local Testing” and “Google OAuth Setup (Login with Google)”.

## Branching, commits, and PRs

- Create a feature branch from `main`
- Keep PRs small and focused; separate unrelated changes
- Write clear, present‑tense commit messages
  - Short summary (max ~72 chars)
  - Optional body with motivation and context
- Reference issues with `Fixes #123` or `Refs #123` when applicable

Example branch names: `feat/cart-merge-guest-session`, `fix/orders-stock-race`, `docs/readme-contributing`.

## Pull request checklist

Please ensure the following before requesting review:

- [ ] Code compiles and runs locally
- [ ] Tests added/updated and passing locally (`pytest -q`)
- [ ] Lint passes (`ruff check .`) and code formatted (`ruff format` if applicable)
- [ ] Database migrations added (if models changed) and applied locally
- [ ] Docs updated (README/inline docs/changelog snippets if relevant)
- [ ] No secrets, tokens, or personal data committed
- [ ] UI changes include screenshots/GIFs when helpful

CI may run additional checks; fix any reported issues.

## Issue reports and discussions

When filing an issue, please include:

- What you expected vs. what happened
- Steps to reproduce (minimal, complete)
- Environment details (OS, Python, Django, browser if UI)
- Relevant logs/tracebacks (redact secrets)

Security issues: avoid public issues. If private reporting is enabled on GitHub, use it; otherwise contact the maintainer via their GitHub profile.

## Project structure highlights

- Django project root: `Django-Shop/` (contains `manage.py`)
- Apps: `cart/`, `orders/`, `products/`, `users/`, `support/`, `careers/`, etc.
- Settings: `Django-Shop/config/settings.py`
- Static and media assets under `Django-Shop/static/` and `Django-Shop/media/`
- Tests live alongside apps (e.g., `Django-Shop/cart/tests/`)

## Thanks

Your time and contributions make this project better. Thank you!
