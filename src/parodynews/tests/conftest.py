import json
import os
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from playwright.sync_api import Page

from parodynews.models import (
    Assistant,
    AssistantGroup,
    ContentDetail,
    ContentItem,
    JSONSchema,
    Message,
    OpenAIModel,
    Post,
    Thread,
)
from parodynews.tests.scripts.functions.user_login import login_user


@pytest.fixture(scope="session")
def e2e_base_url() -> str:
    return os.environ.get("E2E_BASE_URL", "http://localhost:8000").rstrip("/")


@pytest.fixture(scope="session")
def e2e_credentials() -> dict[str, str]:
    username = os.environ.get("E2E_USERNAME", "e2e_user")
    password = os.environ.get("E2E_PASSWORD", "e2e_password")
    email = os.environ.get("E2E_EMAIL", f"{username}@example.com")
    return {"username": username, "password": password, "email": email}


@pytest.fixture(scope="session")
def browser_name() -> str:
    # Enforce Chromium-only for CI determinism.
    return "chromium"


@pytest.fixture(scope="session")
def browser_context_args(e2e_base_url: str) -> dict:
    # pytest-playwright will pass these args to `browser.new_context()`.
    return {"base_url": e2e_base_url}


@pytest.fixture
def logged_in_page(
    page: Page, e2e_base_url: str, e2e_credentials: dict[str, str]
) -> Page:
    # Allauth is configured for email-based authentication.
    ok = login_user(
        page,
        e2e_credentials["email"],
        e2e_credentials["password"],
        base_url=e2e_base_url,
    )
    assert ok, (
        "E2E login failed. Ensure the user exists (recommended: run "
        "`python src/manage.py ensure_e2e_user`)."
    )
    return page


# --------------------------------------------------------------------------- #
# Model fixtures (issue #51)
#
# Two layers, deliberately kept apart:
#
#   *_export   — the REAL exports under `tests/data/`, read as-is. They are flat
#                dumps of production rows, not Django `loaddata` fixtures, so
#                they are read with `json.load` rather than a fixture loader.
#   the rest   — model factories built from those exports where one exists, and
#                from minimal literals where none does.
#
# Factories live here rather than in each test module so that a field rename
# breaks in ONE place. Every one of them depends on `db`, so a test that asks
# for a factory gets database access without repeating the marker.
# --------------------------------------------------------------------------- #
DATA_DIR = Path(__file__).parent / "data"


def _load_export(filename: str):
    """Read one of the `tests/data/*.json` exports."""
    with (DATA_DIR / filename).open() as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def assistant_export() -> list[dict]:
    """46 real Assistant rows exported 2024-11-29."""
    return _load_export("Assistant-2024-11-29.json")


@pytest.fixture(scope="session")
def openai_model_export() -> list[dict]:
    """8 real OpenAIModel rows exported 2024-11-29."""
    return _load_export("OpenAIModel-2024-11-29.json")


@pytest.fixture(scope="session")
def json_schema_export() -> list[dict]:
    """2 real JSONSchema rows exported 2024-10-01.

    Note the `schema` column is exported as a JSON *string*, while the model
    field is a `JSONField` — callers must `json.loads` it.
    """
    return _load_export("JSONSchema-2024-10-01.json")


@pytest.fixture(scope="session")
def default_value_config_export() -> list[dict]:
    """The 2025-02-18 default-value export FieldDefaults rows are built from."""
    return _load_export("DefaultValueConfig-2025-02-18.json")


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        username="model_tester",
        email="model_tester@example.com",
        password="testpass123",
    )


@pytest.fixture
def openai_model(db, openai_model_export) -> OpenAIModel:
    row = openai_model_export[0]
    return OpenAIModel.objects.create(
        model_id=row["model_id"],
        description=row["description"],
    )


@pytest.fixture
def json_schema(db, json_schema_export) -> JSONSchema:
    row = json_schema_export[0]
    return JSONSchema.objects.create(
        name=row["name"],
        description=row["description"],
        schema=json.loads(row["schema"]),
    )


@pytest.fixture
def assistant(db, assistant_export, openai_model, json_schema) -> Assistant:
    """An Assistant built from a real export row.

    The export carries `""` for the two nullable floats and `null` for the three
    JSON columns; both are normalised here so the factory reflects the model's
    field types rather than the exporter's formatting.
    """
    row = assistant_export[0]
    return Assistant.objects.create(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        instructions=row["instructions"],
        prompt=row["prompt"],
        object=row["object"],
        model=openai_model,
        json_schema=json_schema,
        tools=row["tools"] or [],
        metadata=row["metadata"] or {},
        response_format=row["response_format"] or {},
        temperature=row["temperature"] or None,
        top_p=row["top_p"] or None,
    )


@pytest.fixture
def assistant_group(db) -> AssistantGroup:
    return AssistantGroup.objects.create(name="Content Pipeline")


@pytest.fixture
def content_detail(db, user) -> ContentDetail:
    return ContentDetail.objects.create(
        title="Local Cat Declares Independence",
        description="Satirical article about feline autonomy",
        author="ParodyNews Staff",
        slug="cat-independence",
        keywords=["cats", "parody"],
        user=user,
    )


@pytest.fixture
def content_item(db, content_detail, assistant) -> ContentItem:
    return ContentItem.objects.create(
        content_text="In a shocking turn of events...",
        prompt="Write an opening paragraph",
        assistant=assistant,
        detail=content_detail,
    )


@pytest.fixture
def thread(db, assistant_group, user) -> Thread:
    return Thread.objects.create(
        id="thread_model_tests",
        name="Cat Independence Article",
        description="Multi-assistant thread",
        assistant_group=assistant_group,
        user=user,
    )


@pytest.fixture
def message(db, thread, assistant, content_item) -> Message:
    return Message.objects.create(
        id="msg_model_tests",
        thread=thread,
        assistant=assistant,
        contentitem=content_item,
        status="completed",
        run_id="run_model_tests",
    )


@pytest.fixture
def post(db, content_detail, thread, message, assistant, user) -> Post:
    return Post.objects.create(
        content_detail=content_detail,
        thread=thread,
        message=message,
        assistant=assistant,
        post_content="# Breaking News\n\nLocal cat declares independence...",
        filename="2024-01-15-cat-independence.md",
        user=user,
    )
