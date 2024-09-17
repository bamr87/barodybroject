# context_processors.py
from .models import PoweredBy

def footer_items(request):
    return {
        'powered_by': PoweredBy.objects.all()
    }