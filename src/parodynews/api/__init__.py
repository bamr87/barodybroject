"""
File: __init__.py
Description: REST API consumed by the React frontend (Django REST Framework)
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Usage: path("api/", include("parodynews.api.urls"))

Layout:
- ``serializers.py``: model serializers, including nested read-only detail
- ``views.py``: viewsets and the few standalone endpoints (auth/me, site)
- ``pagination.py``: page-number pagination with a client-controlled size
- ``urls.py``: the router
"""
