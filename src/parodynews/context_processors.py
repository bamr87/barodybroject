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
