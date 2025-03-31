# parodynews/management/commands/fetch_models.py
from django.core.management.base import BaseCommand
from openai import OpenAI
from parodynews.models import OpenAIModel

class Command(BaseCommand):
    help = 'Fetch models from OpenAI API and update choices'

    def handle(self, *args, **kwargs):
        client = OpenAI()
        models = client.models.list()
        model_ids = [model.id for model in models]

        for model_id in model_ids:
            OpenAIModel.objects.update_or_create(model_id=model_id)

        self.stdout.write(self.style.SUCCESS('Successfully fetched and saved model choices'))