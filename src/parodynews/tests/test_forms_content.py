"""Tests for the content forms.

Regression coverage for issue #3 — "Assistant Field on ContentFrom not
updating". `ContentItemForm` seeded a default assistant whenever
`self.initial["assistant"]` was falsy. Django builds `self.initial` from
`model_to_dict(instance)`, which yields `assistant: None` for BOTH a brand-new
form AND a saved `ContentItem` whose nullable `assistant` FK is NULL, so the
two cases were indistinguishable and an existing record was treated as new.

`ContentItem.assistant` is `null=True, on_delete=SET_NULL`, so the triggering
state arises on its own whenever a referenced `Assistant` is deleted.
"""

import pytest

from parodynews.forms import ContentItemForm
from parodynews.models import ContentItem


@pytest.fixture
def content_item_without_assistant(db, content_detail) -> ContentItem:
    """A *saved* ContentItem whose `assistant` is NULL."""
    return ContentItem.objects.create(
        content_text="A saved item that has no assistant",
        prompt="Write an opening paragraph",
        assistant=None,
        detail=content_detail,
    )


class TestContentItemFormAssistantSeeding:
    """The default assistant is seeded for new forms only."""

    def test_new_form_seeds_a_default_assistant(self, assistant):
        """An unsaved form still gets a default assistant and its instructions."""
        form = ContentItemForm()

        assert form["assistant"].value() == assistant.id
        assert form["instructions"].value() == assistant.instructions

    def test_existing_item_shows_its_own_assistant(self, content_item, assistant):
        """A saved item WITH an assistant renders that assistant (no regression)."""
        form = ContentItemForm(instance=content_item)

        assert form["assistant"].value() == assistant.id
        assert form["instructions"].value() == assistant.instructions

    def test_saved_item_without_assistant_preselects_nothing(
        self, content_item_without_assistant, assistant
    ):
        """A saved item whose assistant is NULL must not be given one.

        Asserted as "empty", never as "!= this particular assistant": the old
        code picked with `.order_by("?")`, so a value-inequality assertion
        would pass at random.
        """
        form = ContentItemForm(instance=content_item_without_assistant)

        assert not form["assistant"].value()
        assert not form["instructions"].value()

        # The rendered select must offer — and rest on — an empty choice, so
        # the browser cannot submit the first assistant by default.
        rendered = str(form["assistant"])
        assert 'value="" selected>' in rendered
        assert f'value="{assistant.id}" selected' not in rendered

    def test_saving_an_untouched_null_assistant_item_leaves_it_null(
        self, content_item_without_assistant, assistant
    ):
        """Re-saving an unrelated edit must not silently assign an assistant."""
        form = ContentItemForm(
            {
                "assistant": "",
                "instructions": "",
                "prompt": content_item_without_assistant.prompt,
                "content_text": "An edit that has nothing to do with assistants",
            },
            instance=content_item_without_assistant,
        )

        assert form.is_valid(), form.errors
        saved = form.save()

        saved.refresh_from_db()
        assert saved.assistant is None
        assert saved.content_text == "An edit that has nothing to do with assistants"
