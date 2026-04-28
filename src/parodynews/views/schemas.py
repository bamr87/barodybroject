"""
File: schemas.py
Description: Views for managing JSON schemas used by assistants/content generation
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: Included via parodynews URL routing.
"""

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import JSONSchemaForm
from ..models import JSONSchema


def list_schemas(request):
    """Display a list of all JSON schemas."""
    schemas = JSONSchema.objects.all()
    return render(request, "parodynews/schema_detail.html", {"schemas": schemas})


def create_schema(request):
    """Create a new JSON schema."""
    if request.method == "POST":
        form = JSONSchemaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Schema created successfully.")
            return redirect("list_schemas")
    else:
        form = JSONSchemaForm()
    return render(request, "parodynews/schema_form.html", {"form": form})


def edit_schema(request, pk):
    """Edit an existing JSON schema."""
    schema = get_object_or_404(JSONSchema, pk=pk)
    if request.method == "POST":
        form = JSONSchemaForm(request.POST, instance=schema)
        if form.is_valid():
            form.save()
            messages.success(request, "Schema updated successfully.")
            return redirect("list_schemas")
    else:
        form = JSONSchemaForm(instance=schema)
    return render(request, "parodynews/schema_form.html", {"form": form})


def export_schema(request, pk):
    """Export a JSON schema as a downloadable file."""
    schema = get_object_or_404(JSONSchema, pk=pk)
    response = JsonResponse(schema.schema)
    response["Content-Disposition"] = f'attachment; filename="{schema.name}.json"'
    return response


def delete_schema(request, pk):
    """Delete a JSON schema."""
    schema = get_object_or_404(JSONSchema, pk=pk)
    if request.method == "POST":
        schema.delete()
        messages.success(request, "Schema deleted successfully.")
        return redirect("list_schemas")
    return redirect("list_schemas")
