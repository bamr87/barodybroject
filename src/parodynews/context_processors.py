# context_processors.py
"""
Template context shared by the remaining server-rendered pages (auth, profile).

The React app gets the same data from ``GET /api/site/``.
"""

import os
from pathlib import Path

from django.conf import settings

from .models import PoweredBy


def list_issue_templates() -> list[dict[str, str]]:
    """Issue templates under ``.github/ISSUE_TEMPLATE`` as ``{filename, name}``."""
    templates: list[dict[str, str]] = []
    template_dir = Path(settings.BASE_DIR).parent / ".github" / "ISSUE_TEMPLATE"
    if template_dir.exists():
        for fname in sorted(os.listdir(template_dir)):
            if fname.endswith(".md") and fname.lower() != "readme.md":
                label = fname[:-3].replace("_", " ").replace("-", " ").title()
                templates.append({"filename": fname, "name": label})
    return templates


def site_links(request):
    """Footer attribution, the issue shortcut, and the bundled stylesheet.

    The auth pages reuse the React bundle's CSS (Bootstrap plus this app's
    styles) so they need no CDN; `base.html` falls back to the CDN only when
    the frontend has not been built.
    """
    from .views.spa import manifest_assets

    assets = manifest_assets()
    return {
        "powered_by": PoweredBy.objects.all(),
        "github_issue_repo": getattr(settings, "GITHUB_ISSUE_REPO", ""),
        "issue_templates": list_issue_templates(),
        "frontend_styles": assets["styles"] if assets else [],
    }
