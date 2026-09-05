# context_processors.py
import os
from pathlib import Path

from django.conf import settings

from .models import PoweredBy


def footer_items(request):
    return {"powered_by": PoweredBy.objects.all()}


# The environment treatment, in one place: adding `staging` is one row here.
#
# Values are Bootstrap 5.3 semantic classes rather than literal colours, so the
# treatment follows the user's light/dark/auto choice instead of fighting it —
# `text-bg-*` sets a background AND a contrast-appropriate foreground, and both
# are redefined per colour mode.
#
# Production is deliberately absent: it is the unstyled baseline. Colouring the
# normal case too would train everyone to ignore the signal.
ENVIRONMENT_TREATMENTS = {
    "test": {
        "label": "TEST",
        "badge_class": "text-bg-warning",
        "border_class": "border-warning",
    },
    "development": {
        "label": "DEV",
        "badge_class": "text-bg-info",
        "border_class": "border-info",
    },
}


def environment(request):
    """
    Expose the running environment so non-production deployments are
    distinguishable at a glance.

    The label is always rendered as TEXT, never colour alone — colour by itself
    fails for colour-blind users and in greyscale (WCAG 2.1 SC 1.4.1).
    """
    name = getattr(settings, "ENVIRONMENT", "development")
    treatment = ENVIRONMENT_TREATMENTS.get(name)
    return {
        "environment": name,
        # Templates branch on this rather than on `environment == "production"`,
        # so an environment added to the map above needs no template change.
        "show_environment_badge": treatment is not None,
        "environment_label": treatment["label"] if treatment else "",
        "environment_badge_class": treatment["badge_class"] if treatment else "",
        "environment_border_class": treatment["border_class"] if treatment else "",
    }


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
