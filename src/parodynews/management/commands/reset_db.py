import os
import glob
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Deletes the database and migration files to start fresh"

    def handle(self, *args, **kwargs):
        # Define the path to the database file
        db_path = (
            "db.sqlite3"  # Adjust this path if your database file is located elsewhere
        )

        # Define the paths to the migrations directories
        migrations_dirs = [
            "parodynews/migrations",  # Replace 'your_app' with the actual name of your app
            # Add more paths if you have multiple apps
        ]

        # Delete the database file if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.SUCCESS(f"Deleted database file: {db_path}"))
        else:
            self.stdout.write(self.style.WARNING(f"Database file not found: {db_path}"))

        # Delete all migration files in the migrations directories
        for migrations_dir in migrations_dirs:
            migration_files = glob.glob(os.path.join(migrations_dir, "*.py"))
            for migration_file in migration_files:
                if os.path.basename(migration_file) != "__init__.py":
                    os.remove(migration_file)
                    self.stdout.write(
                        self.style.SUCCESS(f"Deleted migration file: {migration_file}")
                    )

            # Also delete the compiled Python files
            migration_pyc_files = glob.glob(
                os.path.join(migrations_dir, "__pycache__", "*.pyc")
            )
            for migration_pyc_file in migration_pyc_files:
                os.remove(migration_pyc_file)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted compiled migration file: {migration_pyc_file}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Database and migrations reset complete."))
