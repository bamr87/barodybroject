# Scripts

Host-side automation for Barodybroject. Django commands should normally run inside the dev container; see [.github/README.md](../.github/README.md) for the current developer workflow.

## Active Scripts

| Script | Purpose |
|---|---|
| [add_current_ip_rule.py](add_current_ip_rule.py) | Add the current public IP to Azure PostgreSQL firewall rules. |
| [azure-deployment-setup.py](azure-deployment-setup.py) | Interactive post-`azd up` Azure setup: migrations, static files, admin user, and health checks. |
| [setup-deployment.sh](setup-deployment.sh) | Thin shell wrapper around `azure-deployment-setup.py`; used by `init_setup.sh`. |
| [test-infrastructure.sh](test-infrastructure.sh) | Validate Docker, database, Django service health, and related infrastructure. |
| [validate-cicd.sh](validate-cicd.sh) | Validate CI/CD workflow assumptions locally. |
| [version-manager.sh](version-manager.sh) | Manage project version metadata. |

## Legacy Candidates

These remain temporarily for compatibility and should be removed after references are migrated:

| Script | Replacement |
|---|---|
| [azure-setup.py](azure-setup.py) | `azure-deployment-setup.py` |
| [setup-azure.sh](setup-azure.sh) | `setup-deployment.sh` / `azd up` |

## Removed Systems

- The generated `README/` mirror and `README.sh` tooling have been removed.
- AWS Aurora setup tooling has been removed; deployment targets Azure Container Apps.