"""
File: spa.py
Description: Serve the React single-page application shell
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Three modes, chosen at request time:

1. ``FRONTEND_DEV_SERVER_URL`` is set (e.g. ``http://localhost:5173``): the
   shell loads ``@vite/client`` and ``src/main.tsx`` straight from the Vite
   dev server, so edits hot-reload while Django keeps serving auth and API.
2. A production build exists (``frontend/dist/.vite/manifest.json``): the
   shell references the hashed bundle through Django's static storage.
3. Neither: a friendly page explains how to build the frontend.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static
from django.views.generic import TemplateView

ENTRY = "src/main.tsx"
STATIC_PREFIX = "frontend/"


@lru_cache(maxsize=4)
def _load_manifest(path: str, mtime: float) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def manifest_assets(dist_dir: Path | str | None = None) -> dict[str, list[str]] | None:
    """Script and stylesheet URLs for the SPA entry, or ``None`` without a build.

    Defaults to ``settings.FRONTEND_DIST_DIR`` so the auth templates can reuse
    the bundle's stylesheet (Bootstrap plus this app's styles) instead of
    pulling Bootstrap from a CDN.
    """
    dist = Path(dist_dir or getattr(settings, "FRONTEND_DIST_DIR", ""))
    manifest_path = dist / ".vite" / "manifest.json"
    if not manifest_path.is_file():
        return None
    manifest = _load_manifest(str(manifest_path), manifest_path.stat().st_mtime)
    entry = manifest.get(ENTRY)
    if not entry:
        return None
    scripts = [static(STATIC_PREFIX + entry["file"])]
    styles = [static(STATIC_PREFIX + css) for css in entry.get("css", [])]
    for imported in entry.get("imports", []):
        chunk = manifest.get(imported, {})
        styles.extend(static(STATIC_PREFIX + css) for css in chunk.get("css", []))
    return {"scripts": scripts, "styles": styles}


class SPAView(TemplateView):
    template_name = "spa/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dev_server = getattr(settings, "FRONTEND_DEV_SERVER_URL", "").rstrip("/")
        dist_dir = Path(getattr(settings, "FRONTEND_DIST_DIR", ""))
        assets = manifest_assets(dist_dir) if dist_dir else None
        context.update(
            {
                "dev_server_url": dev_server,
                "spa_entry": ENTRY,
                "assets": assets,
                "frontend_built": assets is not None,
                "site_name": "Barody Broject",
            }
        )
        return context
