# Archangel Project Documentation

## Overview
Archangel is a Django 5 web application that provides a storefront-style landing page, a custom user authentication flow, and a REST API for tracking narrative titles, characters, and related research materials. The project also contains an auxiliary scraping service for sourcing external data that can be fed into the tracker domain. The codebase is organized to support both local development with the Django development server and deployment via Docker with Gunicorn and Nginx.

## Repository Layout
- `Archangel/` – Core Django project configuration, including settings, URL routing, ASGI/WSGI entry points, and static/media handling.
- `apps/`
  - `mainPage/` – Front page with a static storefront template (`templates/mainPage/main.html`) and product-related models (`models.py`).
  - `users/` – Handles combined registration/login form submission logic via `views.register` and associated templates.
  - `tracker/` – Django REST Framework app exposing CRUD APIs for titles, characters, and parsing materials with serializers and tests.
- `services/`
  - `scraper_service/` – Stand-alone data ingestion utility with a `Dockerfile`, Reddit fetcher (`fetch_reddit.py`), and a modular data processing pipeline (`data_processor/`).
- `static/` and `staticfiles/` – Static assets served locally and collected for production.
- `Dockerfile` and `docker-compose.yaml` – Containerized deployment definition with PostgreSQL, Gunicorn, and Nginx.
- `requirements.txt` – Python dependencies for the Django project and supporting analytics stack.

## Django Applications
### Main Page (`apps/mainPage`)
- **Models**: Defines `Warehouse`, `Employee`, `Product`, `Basket`, and `Comment` for representing inventory, staffing, shopping baskets, and product feedback. (`models.py`)
- **Views**: Renders the storefront template through the `main` view (`views.py`).
- **Templates**: `templates/mainPage/main.html` implements a responsive landing page with category navigation, featured products, and marketing sections.

### Users (`apps/users`)
- **Authentication flow**: The `register` view accepts POST submissions that either register a new user or authenticate an existing one. Validation helpers (`handle_registration`, `handle_login`) enforce unique usernames/emails and use Django’s password hashing utilities (`views.py`).

### Tracker (`apps/tracker`)
- **Models**: `Title`, `Character`, and `ParsingMaterials` capture story worlds, their participants, and research links (`models.py`).
- **Serializers**: `TitleSerializer`, `CharacterSerializer`, and `ParsingMaterialsSerializer` provide DRF serialization with nested read-only relationships and explicit foreign key write fields (`serializers.py`).
- **ViewSets**: Each model is exposed via `ModelViewSet` for full CRUD support (`views.py`).
- **URLs**: The app is mounted under `/api/`, exposing REST endpoints such as `/api/titles/`, `/api/characters/`, and `/api/parsing_materials/` (`apps/tracker/urls.py`).
- **Tests**: Comprehensive API tests located in `apps/tracker/tests/` validate serializers, permissions, and endpoint behavior.

## Services
The `services/scraper_service` package contains an optional ingestion pipeline. It includes:
- `fetch_reddit.py` for downloading external content.
- `data_processor/` modules (`DataCollector`, `dataInitialization`, `dataNormalisation`, `dataProcessor`, `textCleaner`, `wordAnalyser`) to clean and normalize fetched data.
This service can be containerized independently using its Dockerfile and requirements list.

## Configuration
Create a `.env` file alongside `manage.py` with the following variables:
```
SECRET_KEY=
DEBUG=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=
```
When running via Docker Compose, set `DB_HOST=db` to match the PostgreSQL service name. Additional configuration, such as `ALLOWED_HOSTS` or email settings, can be provided through standard Django environment variables recognized in `Archangel/settings.py`.

## Local Development Workflow
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```
3. **Create a superuser (optional but recommended for admin access)**
   ```bash
   python manage.py createsuperuser
   ```
4. **Run the development server**
   ```bash
   python manage.py runserver
   ```
Static files are automatically served when `DEBUG=True`. Media uploads require configuring `MEDIA_ROOT` and ensuring the directory exists.

## Containerized Deployment
The provided Docker setup orchestrates PostgreSQL, the Django application (served by Gunicorn), and Nginx:
1. Build and start the stack:
   ```bash
   docker-compose up --build
   ```
2. Ensure `.env` uses `DB_HOST=db` so the Django container can reach PostgreSQL.
3. Collected static files are mounted into the Nginx container via `./staticfiles`.

The root `Dockerfile` uses a Mambaforge base image, provisions the `Archangel` Conda environment from `archangel_env.yml`, runs `collectstatic`, and launches Gunicorn bound to port 5000.

## API Usage
The REST API is namespaced under `/api/`. Common endpoints include:
- `GET /api/titles/` – List all titles; supports POST for creation.
- `GET /api/characters/` – Retrieve characters; accepts `POST` with `title_id` to assign a parent title.
- `GET /api/parsing_materials/` – Manage external reference links associated with characters via `character_id`.

Each endpoint supports standard DRF pagination, filtering, and browsable API interactions when `DEBUG` is enabled. Authentication/permission settings use DRF defaults and can be customized in `Archangel/settings.py`.

## Testing
Automated tests live primarily under `apps/tracker/tests/`. Run the full suite with:
```bash
python manage.py test
```
Add new tests alongside feature development to maintain coverage across models, serializers, and views.

## Static Assets and Templates
- The storefront UI is defined in `apps/mainPage/templates/mainPage/main.html` and can be extended using Django’s template inheritance.
- Static resources reside in `static/` during development. Use `python manage.py collectstatic` to gather assets into `staticfiles/` for production deployments.

## Additional Notes
- Django Debug Toolbar is enabled when `DEBUG=True`, exposing `/__debug__/` through URL configuration.
- Update `requirements.txt` and `archangel_env.yml` in tandem when adding dependencies to keep Conda and pip environments synchronized.
- The project uses Pillow for image handling (`Product.image`) and expects an accessible media storage backend in production.
