# parodynews/management/commands/fetch_models.py
import json
from django.core.management.base import BaseCommand
from openai import OpenAI
from parodynews.models import Assistant

class Command(BaseCommand):
    help = 'Fetch models from OpenAI API and update choices'

    def handle(self, *args, **kwargs):
        client = OpenAI()
        models = client.models.list()
        model_ids = [model.id for model in models]  # Corrected line
        
        with open('model_choices.json', 'w') as f:
            json.dump(model_ids, f)
        
        self.stdout.write(self.style.SUCCESS('Successfully fetched and saved model choices'))