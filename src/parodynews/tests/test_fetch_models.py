"""
File: test_fetch_models.py
Description: Tests for the `fetch_models` management command (issue #110)
Author: Barodybroject Team <team@example.com>
Created: 2026-09-01
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_fetch_models.py (run from src/)

No test here contacts the live OpenAI API: `Command.get_client` is patched with
a fake in every case, so the suite passes with `OPENAI_API_KEY` unset.
"""

from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase

from parodynews.forms import AssistantForm
from parodynews.management.commands.fetch_models import (
    Command,
    describe_model,
    is_assistant_model,
)
from parodynews.models import Assistant, OpenAIModel

COMMAND_CLIENT = "parodynews.management.commands.fetch_models.Command.get_client"


class FakeModel:
    """One entry of an OpenAI `models.list()` page."""

    def __init__(self, model_id, owned_by="openai", created=1721260800):
        self.id = model_id
        self.owned_by = owned_by
        self.created = created


class FakeModels:
    def __init__(self, ids):
        self._ids = list(ids)

    def list(self):
        return [FakeModel(model_id) for model_id in self._ids]


class FakeClient:
    def __init__(self, ids):
        self.models = FakeModels(ids)


class RaisingClient:
    """A client whose `models.list()` fails, as it does without an API key."""

    class _Models:
        def list(self):
            raise RuntimeError("401 Incorrect API key provided")

    def __init__(self):
        self.models = self._Models()


def fake_client(ids):
    """Return a patch target callable that ignores `self` and yields a fake."""
    return lambda _self: FakeClient(ids)


class IsAssistantModelTests(SimpleTestCase):
    """The filter itself. `SimpleTestCase` — no database, so these run anywhere."""

    def test_chat_models_are_assistant_capable(self):
        for model_id in ("gpt-4o", "gpt-4-turbo", "GPT-4O", "o3-mini"):
            self.assertTrue(is_assistant_model(model_id), model_id)

    def test_other_modalities_are_not(self):
        for model_id in (
            "dall-e-3",
            "tts-1",
            "tts-1-hd",
            "whisper-1",
            "text-embedding-3-large",
            "babbage-002",
            "davinci-002",
            "gpt-3.5-turbo-instruct",
            "gpt-4o-audio-preview",
            "gpt-4o-realtime-preview",
            "gpt-4o-transcribe",
            "gpt-image-1",
            "omni-moderation-latest",
            "",
        ):
            self.assertFalse(is_assistant_model(model_id), model_id)

    def test_description_is_never_empty(self):
        self.assertTrue(describe_model(FakeModel("gpt-4o")).strip())


class FetchModelsCommandTests(TestCase):
    """`manage.py fetch_models` against a faked OpenAI client."""

    # The exact mix the OpenAI `/models` endpoint returns for a real account:
    # image, speech, transcription, embedding and legacy-completion ids
    # alongside the one chat model. Only `gpt-4o` may reach the dropdown.
    MIXED_CATALOGUE = [
        "dall-e-3",
        "tts-1",
        "whisper-1",
        "text-embedding-3-large",
        "babbage-002",
        "gpt-4o",
    ]

    def test_only_assistant_capable_models_are_persisted(self):
        with patch(COMMAND_CLIENT, fake_client(self.MIXED_CATALOGUE)):
            call_command("fetch_models")

        self.assertEqual(
            list(OpenAIModel.objects.values_list("model_id", flat=True)), ["gpt-4o"]
        )

    def test_every_persisted_row_has_a_description(self):
        with patch(COMMAND_CLIENT, fake_client(["gpt-4o", "gpt-4-turbo"])):
            call_command("fetch_models")

        self.assertEqual(OpenAIModel.objects.count(), 2)
        self.assertFalse(
            OpenAIModel.objects.filter(description="").exists(),
            "fetch_models must populate OpenAIModel.description for every row",
        )

    def test_a_delisted_model_is_retired_without_unassigning_its_assistants(self):
        with patch(COMMAND_CLIENT, fake_client(["gpt-4o", "gpt-4-turbo"])):
            call_command("fetch_models")

        retired = OpenAIModel.objects.get(model_id="gpt-4-turbo")
        assistant = Assistant.objects.create(id="asst_retired", model=retired)

        # A later fetch no longer lists gpt-4-turbo.
        with patch(COMMAND_CLIENT, fake_client(["gpt-4o"])):
            call_command("fetch_models")

        assistant.refresh_from_db()
        self.assertEqual(
            assistant.model_id,
            retired.pk,
            "a delisted model must be retired, not deleted — SET_NULL would "
            "silently strip it from every assistant using it",
        )

        retired.refresh_from_db()
        self.assertFalse(retired.is_available)
        self.assertTrue(OpenAIModel.objects.get(model_id="gpt-4o").is_available)

        offered = list(AssistantForm().fields["model"].queryset)
        self.assertNotIn(retired, offered)
        self.assertIn(OpenAIModel.objects.get(model_id="gpt-4o"), offered)

    def test_a_retired_model_becomes_available_again_when_relisted(self):
        with patch(COMMAND_CLIENT, fake_client(["gpt-4o"])):
            call_command("fetch_models")
        with patch(COMMAND_CLIENT, fake_client([])):
            call_command("fetch_models")
        self.assertFalse(OpenAIModel.objects.get(model_id="gpt-4o").is_available)

        with patch(COMMAND_CLIENT, fake_client(["gpt-4o"])):
            call_command("fetch_models")
        self.assertTrue(OpenAIModel.objects.get(model_id="gpt-4o").is_available)

    def test_an_api_error_fails_loudly_and_writes_nothing(self):
        with (
            patch(COMMAND_CLIENT, lambda _self: RaisingClient()),
            self.assertRaises(CommandError) as ctx,
        ):
            call_command("fetch_models")

        self.assertIn("OpenAI API", str(ctx.exception))
        # CommandError is how a management command exits non-zero: Django's
        # ManagementUtility catches it and calls sys.exit(returncode).
        self.assertEqual(ctx.exception.returncode, 1)
        self.assertEqual(
            OpenAIModel.objects.count(),
            0,
            "a failed fetch must leave the model table untouched",
        )

    def test_an_api_error_does_not_retire_already_recorded_models(self):
        with patch(COMMAND_CLIENT, fake_client(["gpt-4o"])):
            call_command("fetch_models")

        with (
            patch(COMMAND_CLIENT, lambda _self: RaisingClient()),
            self.assertRaises(CommandError),
        ):
            call_command("fetch_models")

        self.assertTrue(OpenAIModel.objects.get(model_id="gpt-4o").is_available)

    def test_the_command_builds_a_real_openai_client_by_default(self):
        """`get_client` is the only place the live client is constructed.

        Guards the injection point the rest of this module patches: if it were
        inlined into `handle()` again, these tests would silently start needing
        a live API key.
        """
        with patch("parodynews.management.commands.fetch_models.OpenAI") as openai_ctor:
            self.assertIs(Command().get_client(), openai_ctor.return_value)
