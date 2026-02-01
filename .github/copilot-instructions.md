# Copilot Instructions for Helpdesk Django

## Project Overview
This is a **Django 6.0 helpdesk application** with a PostgreSQL backend. The project uses environment variables via `python-decouple` for configuration. Core structure: `config/` (project settings) + `tickets/` app (ticket management system).

## Key Architecture & Patterns

### Configuration Management
- **Location**: [config/settings.py](config/settings.py)
- **Pattern**: Use `decouple.config()` for all settings (SECRET_KEY, DEBUG, DB_* variables)
- **Environment**: Configuration sourced from `.env` file in project root
- **Critical Settings**:
  - Database: PostgreSQL (not SQLite) - configured via `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
  - Locale: Brazilian Portuguese (pt-br) with São Paulo timezone
  - Debug mode controlled by `DEBUG` environment variable

### URL Routing
- **Root URLconf**: [config/urls.py](config/urls.py)
- **Pattern**: Admin interface at `/admin/` is the only configured endpoint currently
- **Future apps**: Register ticket URLs using `include()` pattern for app-level routing

### Database Configuration
- **Engine**: PostgreSQL (not Django's default SQLite)
- **Schema**: Currently empty; `tickets/` app has no models defined yet
- **Migrations**: Location [tickets/migrations/](tickets/migrations/)
- **Workflow**: 
  1. Define models in [tickets/models.py](tickets/models.py)
  2. Register in [tickets/admin.py](tickets/admin.py) for admin interface
  3. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### App Structure
- **tickets/** is the primary domain app for helpdesk functionality
- Models, views, and admin customizations belong here
- Each model should have corresponding admin registration for data management

## Development Workflow

### Virtual Environment & Setup
```bash
# Activate venv (Windows)
venv\Scripts\activate

# Run server
python manage.py runserver

# Create superuser for admin
python manage.py createsuperuser

# Database migrations
python manage.py makemigrations
python manage.py migrate
```

### Required Environment Variables
- `SECRET_KEY`: Django secret (current value in `.env` is unsafe for production)
- `DEBUG`: Set to `True` for development, `False` for production
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL connection details

## Common Tasks & Patterns

### Adding a New Model
1. Define in [tickets/models.py](tickets/models.py) (currently empty)
2. Register in [tickets/admin.py](tickets/admin.py) for admin interface
3. Run `python manage.py makemigrations tickets`
4. Run `python manage.py migrate`

### Middleware & Security
- CSRF protection enabled
- Session middleware configured
- SecurityMiddleware applied (Django best practice)
- No ALLOWED_HOSTS configured yet - will need update for deployment

## Dependencies
- Django 6.0.1
- python-decouple (for environment config)
- psycopg2 (PostgreSQL adapter - required for DB operations)

## Important Notes for Agents
- **Models are empty**: The `tickets/models.py` is a blank slate - you'll likely need to create Ticket, User, Comment, or similar domain models
- **Admin registration required**: Every model needs explicit registration in [tickets/admin.py](tickets/admin.py) to appear in admin interface
- **No REST API configured**: Current setup is Django ORM + admin interface; no DRF (Django REST Framework) is installed
- **Static files not configured**: `STATIC_URL` is set but `STATIC_ROOT` not defined - needed for production
- **No templates configured**: `TEMPLATES` has `APP_DIRS: True` but no custom paths - templates go in `tickets/templates/`

## Testing
- Test file exists at [tickets/tests.py](tickets/tests.py) (currently empty)
- Run tests: `python manage.py test tickets`

---
**Last Updated**: January 2026 | **Django Version**: 6.0.1
