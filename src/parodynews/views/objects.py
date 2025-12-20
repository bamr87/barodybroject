"""
File: objects.py
Description: Generic CRUD views for object management
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: Included via parodynews URL routing.
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View

from ..forms import MyObjectForm
from ..models import MyObject


class MyObjectView(View):
    """Generic object management view for demonstration purposes."""

    template_name = "object_template.html"
    success_url = reverse_lazy("object-list")

    def get(self, request, pk=None, action=None):
        """Handle GET requests for object management operations."""
        if action == "delete" and pk:
            obj = get_object_or_404(MyObject, pk=pk)
            return render(
                request,
                self.template_name,
                {
                    "object": obj,
                    "object_list": MyObject.objects.all(),
                    "action": "delete",
                },
            )

        if pk:
            obj = get_object_or_404(MyObject, pk=pk)
            form = MyObjectForm(instance=obj)
            action = "update"
        else:
            form = MyObjectForm()
            obj = None
            action = "create"

        objects = MyObject.objects.all()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "object": obj,
                "object_list": objects,
                "action": action,
            },
        )

    def post(self, request, pk=None, action=None):
        """Handle POST requests for object management operations."""
        if action == "delete" and pk:
            obj = get_object_or_404(MyObject, pk=pk)
            obj.delete()
            return redirect(self.success_url)

        if pk:
            obj = get_object_or_404(MyObject, pk=pk)
            form = MyObjectForm(request.POST, instance=obj)
            action = "update"
        else:
            form = MyObjectForm(request.POST)
            obj = None
            action = "create"

        if form.is_valid():
            form.save()
            return redirect(self.success_url)

        objects = MyObject.objects.all()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "object": obj,
                "object_list": objects,
                "action": action,
            },
        )

