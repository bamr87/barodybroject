from django.apps import AppConfig


class ParodynewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "parodynews"


INSTALLED_APPS = [
    # Other apps
    "parodynews.apps.ParodynewsConfig",  # This is how you reference your custom app
    # Django apps...
]
