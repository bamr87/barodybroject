# context_processors.py
import os
from pathlib import Path

from django.conf import settings

from .models import PoweredBy


def footer_items(request):
    return {"powered_by": PoweredBy.objects.all()}


def issue_templates(request):
    """
    Provides a list of issue template filenames and human-readable names,
    and the GitHub repo setting, for populating the report issue dropdown.
    """
    repo = getattr(settings, "GITHUB_ISSUE_REPO", "")
    templates = []
    # .github/ISSUE_TEMPLATE folder is one level above BASE_DIR
    template_dir = Path(settings.BASE_DIR).parent / ".github" / "ISSUE_TEMPLATE"
    if template_dir.exists():
        for fname in sorted(os.listdir(template_dir)):
            if fname.endswith(".md"):
                label = fname[:-3].replace("_", " ").replace("-", " ").title()
                templates.append({"filename": fname, "name": label})
    return {
        "issue_templates": templates,
        "github_issue_repo": repo,
    }


def fleet_feedback(request):
    """
    Expose the <fleet-feedback> widget's configuration to every template.

    Read by ``templates/includes/fleet_feedback.html``. None of these values is
    a credential: the widget runs in ``url`` mode, so it only ever builds a
    ``github.com/.../issues/new?...`` link and lets GitHub's own session
    authenticate the reporter.

    ``FLEET_ENV`` is derived here rather than in the template because Django's
    built-in ``debug`` context processor only sets its flag when the request IP
    is in ``INTERNAL_IPS``, which would mislabel ordinary local development as
    production.
    """
    return {
        "FLEET_REPO": getattr(settings, "FLEET_REPO", ""),
        "FLEET_BRANCH": getattr(settings, "FLEET_BRANCH", "") or "main",
        "FLEET_ENV": "development" if settings.DEBUG else "production",
    }
