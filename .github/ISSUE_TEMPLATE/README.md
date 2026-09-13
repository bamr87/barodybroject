
# ISSUE_TEMPLATE Directory

## Purpose
This directory contains GitHub issue templates that standardize the process of reporting bugs, requesting features, and documenting technical requirements. These templates guide contributors through providing essential information for effective issue resolution and feature development.

## Contents
- `bug_report.md`: Template for reporting bugs with reproduction steps, environment details, and expected behavior
- `custom.md`: Generic custom issue template for issues that don't fit other categories
- `feature_request.md`: General feature request template for new functionality proposals
- `feature_request_functional_requirements.md`: Detailed functional requirements template for complex features
- `feature_request_functional_test.md`: Template for requesting functional testing scenarios
- `feature_request_technical_requirements.md`: Technical specifications template for implementation details
- `feature_request_technical_tests.md`: Template for technical testing requirements and acceptance criteria
- `issue_detail_template.md`: Comprehensive issue template with detailed information gathering
- `issue_template.md`: Basic issue template for general problem reporting
- `page_feedback.yml`: Structured form behind the app's in-app "Improve this page" control — the no-JavaScript twin of the `<fleet-feedback>` widget mounted in `base.html`

## In-app feedback vs. a hand-filed issue

`page_feedback.yml` is the only template here that is normally reached from *inside the running application* rather than from GitHub's "New issue" screen. It exists in two forms:

- **With JavaScript** — the `<fleet-feedback>` widget builds a prefilled issue
URL that already contains the page URL and view name, the reporter's browser and OS, and any console errors captured before the dialog was opened. The reporter only writes the description.
- **Without JavaScript** — the inline "Improve this page" anchor links straight
  to this form, which asks for the same information by hand.

Either way the issue is labelled `page-feedback` plus a type label, and its body ends with a `<!-- fleet-feedback v1 type=... -->` marker. That marker and label are what distinguish it from a hand-filed issue: the context is machine-collected rather than remembered, so it is usually reproducible without a follow-up question. See the repository README's "In-app feedback" section.

## Usage
Templates are automatically presented when creating new GitHub issues:

```markdown
<!-- Example bug report structure -->
## Bug Description
A clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. See error

## Expected Behavior
What should happen.

## Environment
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Django Version: [e.g. 4.2]
```

Template categories:
- **Bug Reports**: Structured bug reporting with reproduction steps
- **Feature Requests**: Various levels of feature request detail
- **Technical Requirements**: Detailed technical specifications
- **Testing Templates**: Test case and scenario documentation
- **General Issues**: Flexible templates for various issue types

## Container Configuration
Issue templates are not container-specific but support development workflow:
- Templates guide proper issue reporting for containerized environments
- Include environment details relevant to Docker and Azure deployment
- Support for both development container and production container issues

## Related Paths
- Incoming: Used by community contributors and developers when creating GitHub issues
- Outgoing: Guides issue creation process to improve development workflow and bug resolution
