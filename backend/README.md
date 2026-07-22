# OTA Backend Foundation

## Getting started

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```
4. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Included components
- Django project skeleton
- DRF and OpenAPI support
- MySQL, Redis, and Celery configuration
- Health check endpoint and initial app structure
- Docker and CI scaffolding
