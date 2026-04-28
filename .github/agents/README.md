# GitHub Agents

This directory contains optional custom agents for repository maintenance. Keep these files focused on repeatable workflows that are still actively used.

## Available Agents

| Agent | File | Purpose |
|---|---|---|
| Infrastructure Tester | [infra-tester.md](infra-tester.md) | Validate Docker, infrastructure, and test automation. |
| Workflow Reviewer | [workflow-reviewer.md](workflow-reviewer.md) | Review GitHub Actions failures and recommend fixes. |

## Maintenance Rules

- Do not regenerate the deleted `README/` mirror tree.
- Do not add one-off implementation summaries as agents; keep historical reports in issue or PR history.
- Keep agent docs linked to current scripts, workflows, and commands only.