"""Tests for the post publication route's error reporting.

Regression coverage for issue #114 — "Any errors encountered during the
publication process are clearly communicated to the user".

Two defects are covered, both in `services.publishing`:

1. A GitHub failure produced no message a reader could act on. Only
   `PublishingNotConfigured` was distinguished; everything else fell through
   to a generic `Publishing failed: <repr>`.
2. Worse than uncaught — *swallowed*. `repo.get_contents()` and
   `repo.update_file()` shared one `except GithubException:` whose handler
   called `create_file()`. Any failure — an expired token, an exhausted rate
   limit — was therefore answered by a second, unrelated write, and the
   reader was told something about file creation. Only a **404** means "no
   such file yet".

The service is driven directly (it is where the translation lives) and the
API endpoint is driven through DRF (it is what the React UI calls), so both
halves of the path are asserted.
"""

from unittest.mock import MagicMock, patch

import pytest
from github.GithubException import GithubException

from parodynews.models import AppConfig
from parodynews.services import publishing as publishing_services

REPO = "bamr87/it-journey"

pytestmark = pytest.mark.django_db


@pytest.fixture
def app_config(db) -> AppConfig:
    return AppConfig.objects.create(
        github_pages_repo=REPO,
        github_pages_branch="main",
        github_pages_token="ghp_a_test_token",
        github_pages_post_dir="posts/",
    )


def _repo_stub(branch_exists=True):
    """A GitHub repo double on which everything succeeds by default."""
    repo = MagicMock()

    def get_branch(name):
        if name == "main" or branch_exists:
            return MagicMock()
        raise GithubException(404, {"message": "Branch not found"}, None)

    repo.get_branch.side_effect = get_branch
    repo.create_pull.return_value.html_url = f"https://github.com/{REPO}/pull/7"
    return repo


def _publish(post):
    """Run the real service call, returning the `PublicationError` it raises."""
    with pytest.raises(publishing_services.PublicationError) as caught:
        publishing_services.publish_post(post)
    return caught.value


# --------------------------------------------------------------------------- #
# Each GitHub failure becomes a message naming what to change
# --------------------------------------------------------------------------- #
@patch("github.Github")
def test_a_bad_credential_names_the_token(github, post, app_config):
    github.return_value.get_repo.side_effect = GithubException(
        401, {"message": "Bad credentials"}, None
    )

    message = _publish(post).message.lower()

    assert "token" in message
    assert "401" in message


@patch("github.Github")
def test_a_missing_repository_names_the_repository(github, post, app_config):
    github.return_value.get_repo.side_effect = GithubException(
        404, {"message": "Not Found"}, None
    )

    message = _publish(post).message

    assert REPO in message
    assert "main" in message


@patch("github.Github")
def test_a_rate_limit_is_reported_as_itself(github, post, app_config):
    """The shared `except GithubException` used to answer a 403 by creating a file."""
    repo = _repo_stub()
    repo.get_contents.side_effect = GithubException(
        403, {"message": "API rate limit exceeded"}, None
    )
    github.return_value.get_repo.return_value = repo

    error = _publish(post)

    assert "rate limit" in error.message.lower()
    repo.create_file.assert_not_called()
    repo.update_file.assert_not_called()
    repo.create_pull.assert_not_called()


@patch("github.Github")
def test_a_failed_update_is_not_retried_as_a_create(github, post, app_config):
    """`update_file` failing must not fall through to `create_file`."""
    repo = _repo_stub()
    repo.get_contents.return_value = MagicMock(sha="deadbeef")
    repo.update_file.side_effect = GithubException(
        409, {"message": "is at 1234 but expected 5678"}, None
    )
    github.return_value.get_repo.return_value = repo

    error = _publish(post)

    assert "write" in error.message.lower()
    repo.create_file.assert_not_called()
    repo.create_pull.assert_not_called()


@patch("github.Github")
def test_a_branch_lookup_failure_does_not_create_a_branch(github, post, app_config):
    """Only a 404 from `get_branch` means "not there yet"."""
    repo = MagicMock()

    def get_branch(name):
        if name == "main":
            return MagicMock()
        raise GithubException(403, {"message": "API rate limit exceeded"}, None)

    repo.get_branch.side_effect = get_branch
    github.return_value.get_repo.return_value = repo

    error = _publish(post)

    assert "rate limit" in error.message.lower()
    repo.create_git_ref.assert_not_called()


@patch("github.Github")
def test_an_existing_pull_request_is_reported_with_its_link(github, post, app_config):
    repo = _repo_stub()
    repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"}, None)
    repo.create_pull.side_effect = GithubException(
        422, {"message": "A pull request already exists"}, None
    )

    existing = MagicMock()
    existing.head.ref = f"publish/{post.id}-v1"
    existing.html_url = f"https://github.com/{REPO}/pull/3"
    repo.get_pulls.return_value = [existing]
    github.return_value.get_repo.return_value = repo

    error = _publish(post)

    assert "already open" in error.message.lower()
    assert f"https://github.com/{REPO}/pull/3" in error.message
    assert error.url == f"https://github.com/{REPO}/pull/3"


@patch("github.Github")
def test_an_unlinkable_422_still_explains_itself(github, post, app_config):
    """Looking up the open PR is best-effort; its failure must not mask the 422."""
    repo = _repo_stub()
    repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"}, None)
    repo.create_pull.side_effect = GithubException(
        422, {"message": "No commits between main and publish"}, None
    )
    repo.get_pulls.side_effect = GithubException(403, {"message": "Forbidden"}, None)
    github.return_value.get_repo.return_value = repo

    error = _publish(post)

    assert error.url is None
    assert "No commits between main and publish" in error.message


# --------------------------------------------------------------------------- #
# The happy path still publishes
# --------------------------------------------------------------------------- #
@patch("github.Github")
def test_a_new_file_is_created_and_the_pull_request_url_returned(
    github, post, app_config
):
    repo = _repo_stub()
    repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"}, None)
    github.return_value.get_repo.return_value = repo

    version, url = publishing_services.publish_post(post)

    repo.create_file.assert_called_once()
    repo.update_file.assert_not_called()
    assert url == f"https://github.com/{REPO}/pull/7"
    assert version.version_number == 1
    post.refresh_from_db()
    assert post.status == "published"


@patch("github.Github")
def test_an_existing_file_is_updated_rather_than_created(github, post, app_config):
    repo = _repo_stub()
    repo.get_contents.return_value = MagicMock(sha="deadbeef")
    github.return_value.get_repo.return_value = repo

    _, url = publishing_services.publish_post(post)

    repo.update_file.assert_called_once()
    repo.create_file.assert_not_called()
    assert url == f"https://github.com/{REPO}/pull/7"


# --------------------------------------------------------------------------- #
# The API hands the message to the client instead of a stack trace
# --------------------------------------------------------------------------- #
@patch("github.Github")
def test_the_publish_endpoint_returns_the_message_not_a_500(
    github, api_client, post, app_config
):
    github.return_value.get_repo.side_effect = GithubException(
        401, {"message": "Bad credentials"}, None
    )

    response = api_client.post(f"/api/posts/{post.id}/publish/", {}, format="json")

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert "token" in detail.lower()
    assert not detail.startswith("Publishing failed")


@patch("github.Github")
def test_the_publish_endpoint_passes_through_the_existing_pull_request_link(
    github, api_client, post, app_config
):
    repo = _repo_stub()
    repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"}, None)
    repo.create_pull.side_effect = GithubException(
        422, {"message": "A pull request already exists"}, None
    )
    existing = MagicMock()
    existing.head.ref = f"publish/{post.id}-v1"
    existing.html_url = f"https://github.com/{REPO}/pull/3"
    repo.get_pulls.return_value = [existing]
    github.return_value.get_repo.return_value = repo

    response = api_client.post(f"/api/posts/{post.id}/publish/", {}, format="json")

    assert response.status_code == 502
    assert response.json()["url"] == f"https://github.com/{REPO}/pull/3"


def test_an_unconfigured_deployment_is_still_a_400(api_client, post):
    """The one path that already worked keeps its 400 rather than a 502."""
    response = api_client.post(f"/api/posts/{post.id}/publish/", {}, format="json")

    assert response.status_code == 400
    assert "not configured" in response.json()["detail"].lower()
