# Modular Monolith Django Architecture

**A reusable full-stack starter template built with Django, Django REST Framework, React, TypeScript, and Vite.**

[Lire la documentation en français](README.fr.md)

## Overview

This repository provides a structured foundation for building full-stack web applications. It separates the Django backend from the React frontend while keeping the backend organized into modular Django applications.

The goal is to reduce setup time, encourage maintainable code, and provide a consistent structure for future projects.

## Tech Stack

### Backend
- **Python** — Backend programming language.
- **Django** — Web framework and ORM.
- **Django REST Framework (DRF)** — REST API development, serialization, validation, and permissions.
- **SQLite / PostgreSQL** — Database options, depending on the project configuration.

### Frontend
- **React** — UI library.
- **TypeScript** — Static typing.
- **Vite** — Development server and build tool.
- **ESLint** — Code quality and linting.

## Project Structure

```text
.
├── apps/
│   └── <app_name>/
│       ├── migrations/
│       ├── tests/
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── queries.py
│       ├── serializers.py
│       ├── services.py
│       ├── urls.py
│       └── views.py
├── common/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── docs/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── scripts/
├── web/
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/
│       ├── hooks/
│       ├── types/
│       └── main.tsx
├── .env.example
├── .gitignore
├── manage.py
└── README.md
```

## Architecture

The project follows a **modular monolith architecture with a layered organization**.

Each Django application represents a specific business domain and contains the code related to that domain. The frontend is maintained separately in the `web/` directory.

### Backend responsibilities

| File | Responsibility |
|---|---|
| `models.py` | Defines database models and relationships using the Django ORM. |
| `queries.py` | Groups reusable or complex database read operations. |
| `services.py` | Implements business operations and use cases. |
| `serializers.py` | Handles API data serialization, deserialization, and input validation. |
| `views.py` | Handles HTTP requests and returns API responses. |
| `urls.py` | Maps URL patterns to views. |
| `admin.py` | Configures Django admin interfaces. |
| `apps.py` | Defines the Django application configuration. |
| `migrations/` | Stores database schema migrations. |
| `tests/` | Contains automated tests. |

### Design principles

- **Separation of concerns:** each module has a clearly defined responsibility.
- **Modularity:** business domains are separated into Django applications.
- **Reusability:** shared code belongs in `common/` when it is genuinely used across domains.
- **Maintainability:** business logic should not accumulate inside views.
- **Testability:** queries and business operations can be tested independently where appropriate.

This structure is inspired by layered architecture and Clean Architecture principles, without enforcing a strict Clean Architecture implementation.

## Prerequisites

Make sure you have the following installed:

- Python 3.12 or another version supported by the project's dependencies.
- Node.js and npm.
- Git.

Check your installed versions:

```bash
python --version
node --version
npm --version
git --version
```

## Getting Started

### 1. Create a repository from this template

On GitHub, open this repository and select **Use this template → Create a new repository**.

Alternatively, clone the repository directly:

```bash
git clone https://github.com/OWNER/REPOSITORY.git
cd REPOSITORY
```

Replace `OWNER/REPOSITORY` with the actual repository path.

### 2. Set up the backend

Create and activate a Python virtual environment from the project root.

**Windows — PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements/development.txt
```

Make sure `requirements/development.txt` includes the base requirements, for example:

```text
-r base.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in the required values.

**Windows — PowerShell**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS**

```bash
cp .env.example .env
```

Keep secrets, passwords, and production credentials out of version control.

**Important:** Django does not load `.env` files automatically. Ensure the project is configured to load them using the chosen environment-variable library or another explicit configuration mechanism.

### 4. Run database migrations

```bash
python manage.py migrate
```

Create an administrator account if needed:

```bash
python manage.py createsuperuser
```

### 5. Start the backend

```bash
python manage.py runserver
```

The development server is available at:

- Backend: `http://127.0.0.1:8000/`
- Django admin: `http://127.0.0.1:8000/admin/`

The actual API endpoints depend on the URL configuration of the project.

### 6. Set up the frontend

Open a second terminal:

```bash
cd web
npm install
npm run dev
```

Vite will display the local frontend URL in the terminal, usually `http://localhost:5173/`.

## Creating a Django Application

Create a new application inside `apps/`:

```bash
python manage.py startapp projects apps/projects
```

Then:

1. Ensure `apps/` is a Python package by adding `apps/__init__.py` if necessary.
2. Check `apps/projects/apps.py` and configure the correct `AppConfig` name, such as `apps.projects`.
3. Register the application in the appropriate Django settings module.
4. Add models, queries, services, serializers, views, URLs, and tests as needed.
5. Include the application URLs in `config/urls.py`.

For example:

```python
from django.urls import include, path

urlpatterns = [
    path("api/projects/", include("apps.projects.urls")),
]
```

Adapt the URL prefix to the API design of your project.

## Testing

Run the Django test suite:

```bash
python manage.py test
```

Tests can be organized by responsibility, for example:

- `test_models.py` — model behavior and constraints.
- `test_queries.py` — database read operations.
- `test_services.py` — business rules and use cases.

For the frontend, configure and run the test framework selected for the project.

## Production Considerations

Before deploying an application:

- Set `DEBUG = False`.
- Configure `ALLOWED_HOSTS`.
- Store secrets in environment variables or a dedicated secrets manager.
- Use a production-ready database, such as PostgreSQL, when appropriate.
- Configure static files and media storage.
- Configure HTTPS and secure cookies.
- Run Django's deployment checks:

```bash
python manage.py check --deploy
```

- Build the frontend:

```bash
cd web
npm run build
```

The production deployment strategy must define how the frontend build is served and how API requests are routed to Django.

---
**Documentation:** [English](README.md) · [Français](README.fr.md)
