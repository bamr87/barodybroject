import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Refresh migration files based on DB_CHOICE. If using sqlite, remove migrations and create new ones.'

    def handle(self, *args, **options):
        db_choice = os.environ.get("DB_CHOICE", "postgres")
        if db_choice == "sqlite":
            self.stdout.write("SQLite selected. Removing existing migration files and recreating migrations...")
            # List your project apps that need migration refresh
            apps = ['parodynews']  # Add more app names as needed
            for app in apps:
                migrations_dir = os.path.join(settings.BASE_DIR, app, 'migrations')
                if os.path.exists(migrations_dir):
                    for filename in os.listdir(migrations_dir):
                        if filename.endswith(".py") and filename != "__init__.py":
                            file_path = os.path.join(migrations_dir, filename)
                            self.stdout.write(f"Removing: {file_path}")
                            os.remove(file_path)
            self.stdout.write("Running makemigrations...")
            os.system("python manage.py makemigrations")
        else:
            self.stdout.write("Postgres selected. No migration refresh necessary.")
