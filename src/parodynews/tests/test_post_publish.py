"""Tests for the post publication route.

Regression coverage for issue #114 — "Any errors encountered during the
publication process are clearly communicated to the user". Every GitHub API
failure in `push_to_github_and_create_pr()` used to propagate uncaught out of
`ManagePostView.publish()`, so the reader got a 500 instead of a message. One
path was worse: a bare `except Exception` around `repo.get_contents()` turned
*any* failure — including a rate limit — into a `create_file()` call that then
failed with an unrelated error.

These drive the real route, `POST /posts/` with `_method=publish`, and assert on
the messages the reader actually sees.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone
from github.GithubException import GithubException

from parodynews.models import AppConfig, PostFrontMatter

REPO = "bamr87/it-journey"


@pytest.fixture
def app_config(db) -> AppConfig:
    return AppConfig.objects.create(
        api_key="test-api-key",
        project_id="test-project",
        org_id="test-org",
        github_pages_repo=REPO,
        github_pages_branch="main",
        github_pages_token="ghp_a_test_token",
        github_pages_post_dir="posts/",
    )


@pytest.fixture
def publishable_post(db, post):
    """The `post` factory plus the front matter publication requires."""
    PostFrontMatter.objects.create(
        post=post,
        title="Local Cat Declares Independence",
        description="Satirical article about feline autonomy",
        author="ParodyNews Staff",
        published_at=timezone.now(),
        slug="cat-independence",
    )
    return post


@pytest.fixture
def author_client(client, user):
    client.force_login(user)
    return client


def _publish(author_client, post_id):
    return author_client.post(
        reverse("manage_post"), {"_method": "publish", "post_id": post_id}
    )


def _messages(response):
    return " ".join(str(m) for m in get_messages(response.wsgi_request))


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


@pytest.mark.django_db
class TestPublishReportsGithubFailures:
    """No GitHub failure may leave the view by raising."""

    @patch("parodynews.views.posts.Github")
    def test_bad_credential_is_reported_not_raised(
        self, github, author_client, publishable_post, app_config
    ):
        github.return_value.get_repo.side_effect = GithubException(
            401, {"message": "Bad credentials"}, None
        )

        response = _publish(author_client, publishable_post.id)

        assert response.status_code == 302
        assert response.url == reverse("manage_post")
        text = _messages(response).lower()
        assert "token" in text or "credential" in text

    @patch("parodynews.views.posts.Github")
    def test_rate_limit_is_reported_and_does_not_trigger_create_file(
        self, github, author_client, publishable_post, app_config
    ):
        """The bare `except Exception` used to answer a 403 by creating a file."""
        repo = _repo_stub()
        repo.get_contents.side_effect = GithubException(
            403, {"message": "API rate limit exceeded"}, None
        )
        github.return_value.get_repo.return_value = repo

        response = _publish(author_client, publishable_post.id)

        assert response.status_code == 302
        assert response.url == reverse("manage_post")
        repo.create_file.assert_not_called()
        repo.update_file.assert_not_called()
        repo.create_pull.assert_not_called()
        assert "rate limit" in _messages(response).lower()

    @patch("parodynews.views.posts.Github")
    def test_existing_pull_request_is_reported_with_its_link(
        self, github, author_client, publishable_post, app_config
    ):
        repo = _repo_stub()
        repo.get_contents.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )
        repo.create_pull.side_effect = GithubException(
            422, {"message": "A pull request already exists"}, None
        )

        branch = f"publish/{publishable_post.id}-v1"
        existing = MagicMock()
        existing.head.ref = branch
        existing.html_url = f"https://github.com/{REPO}/pull/3"
        repo.get_pulls.return_value = [existing]

        github.return_value.get_repo.return_value = repo

        response = _publish(author_client, publishable_post.id)

        assert response.status_code == 302
        assert response.url == reverse("manage_post")
        text = _messages(response)
        assert "already open" in text.lower()
        assert f"https://github.com/{REPO}/pull/3" in text

    @patch("parodynews.views.posts.Github")
    def test_missing_repository_is_reported(
        self, github, author_client, publishable_post, app_config
    ):
        github.return_value.get_repo.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )

        response = _publish(author_client, publishable_post.id)

        assert response.status_code == 302
        assert REPO in _messages(response)


@pytest.mark.django_db
class TestPublishReportsLocalFailures:
    """The lookups before GitHub is reached must not 500 either."""

    @patch("parodynews.views.posts.Github")
    def test_missing_post_is_reported(
        self, github, author_client, publishable_post, app_config
    ):
        response = _publish(author_client, publishable_post.id + 9999)

        assert response.status_code == 302
        assert response.url == reverse("manage_post")
        assert "no longer exists" in _messages(response).lower()
        github.assert_not_called()

    @patch("parodynews.views.posts.Github")
    def test_missing_front_matter_is_reported(
        self, github, author_client, post, app_config
    ):
        """`post` has no PostFrontMatter — the `publishable_post` fixture adds it."""
        response = _publish(author_client, post.id)

        assert response.status_code == 302
        assert response.url == reverse("manage_post")
        assert "front matter" in _messages(response).lower()
        github.assert_not_called()

    def test_missing_configuration_is_reported(self, author_client, publishable_post):
        """No AppConfig row at all — the one path that already worked."""
        response = _publish(author_client, publishable_post.id)

        assert response.status_code == 302
        assert response.url == reverse("manage_post")
        assert "configuration is missing" in _messages(response).lower()


@pytest.mark.django_db
class TestPublishStillPublishes:
    """The error handling must not have broken the happy path."""

    @patch("parodynews.views.posts.Github")
    def test_new_post_is_created_and_redirects_to_the_pull_request(
        self, github, author_client, publishable_post, app_config
    ):
        repo = _repo_stub()
        repo.get_contents.side_effect = GithubException(
            404, {"message": "Not Found"}, None
        )
        github.return_value.get_repo.return_value = repo

        response = _publish(author_client, publishable_post.id)

        repo.create_file.assert_called_once()
        repo.update_file.assert_not_called()
        assert response.status_code == 302
        assert response.url == f"https://github.com/{REPO}/pull/7"

    @patch("parodynews.views.posts.Github")
    def test_existing_file_is_updated_rather_than_created(
        self, github, author_client, publishable_post, app_config
    ):
        repo = _repo_stub()
        repo.get_contents.return_value = MagicMock(sha="deadbeef")
        github.return_value.get_repo.return_value = repo

        response = _publish(author_client, publishable_post.id)

        repo.update_file.assert_called_once()
        repo.create_file.assert_not_called()
        assert response.url == f"https://github.com/{REPO}/pull/7"
