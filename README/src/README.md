# src/ Directory

## Purpose
This is the main source code directory for the Django-based parody news generator application.

## Contents
- `_data/`: Data files for the application (has its own README)
- `404.html`: Custom 404 page
- `apprunner.yaml`: AWS App Runner configuration
- `assets/`: Static assets (images, js)
- `azure.yaml`: Azure configuration
- `barodybroject/`: Django project settings
- `db.sqlite3`: Development database
- `docker-compose.yml`: Docker composition
- `Dockerfile`: Container definition
- `docs/`: Documentation files
- `entrypoint.sh`: Container entrypoint
- `favicon.ico`: Site favicon
- `gunicorn.conf.py`: Gunicorn config
- `index.md`: Index page
- `manage.py`: Django management script
- `pages/`: Site pages and configs
- `parodynews/`: Main Django app
- `requirements.txt`: Python dependencies
- `scripts/`: Additional scripts
- `src_env/`: Virtual environment
- `static/`: Static files
- And other files/subdirs

## Usage
Run the development server: python manage.py runserver

## Container Configuration
See Dockerfile for build instructions.

## Related Paths
- Incoming: From project root
- Outgoing: To deployment scripts
