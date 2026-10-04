"""Shared fixtures for the legacy test/ suite (run by scripts/test-infrastructure.sh)."""

from pathlib import Path

import pytest
from setup.services import InstallationService


@pytest.fixture(autouse=True)
def isolated_installation_state(tmp_path, monkeypatch):
    """Point every InstallationService at a per-test temp dir.

    The service keeps its state in files: `.installation` under BASE_DIR (the
    repo ships one marked complete) and the setup-token config. Without this,
    tests read the committed "installation complete" marker and leak tokens
    into each other.
    """
    original_init = InstallationService.__init__

    def init(self):
        original_init(self)
        self.installation_file = Path(tmp_path) / ".installation"
        self.config_file = Path(tmp_path) / "setup_config.json"

    monkeypatch.setattr(InstallationService, "__init__", init)
    yield tmp_path
