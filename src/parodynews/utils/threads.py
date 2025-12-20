"""
File: threads.py
Description: Thread and message helper functions for OpenAI assistant workflows
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- openai: >=1.57.0

Usage: from parodynews.utils.threads import create_thread
"""

import json
import time


def openai_create_message(client, contentitem):
    """
    Create a new thread and message for content processing.

    Args:
        client: OpenAI client instance
        contentitem: ContentItem model instance

    Returns:
        tuple: (message, thread_id) - OpenAI message object and thread ID
    """
    thread = client.beta.threads.create(
        metadata={
            "type": "news_article_thread",
            "title": contentitem.detail.title,
            "description": contentitem.detail.description,
        },
    )
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=contentitem.content_text
    )
    return message, thread.id


def openai_delete_message(client, message_id, thread_id):
    """
    Delete a specific message from an OpenAI thread.

    Args:
        client: OpenAI client instance
        message_id: Unique identifier of message to delete
        thread_id: Thread containing the message

    Returns:
        dict: Deletion confirmation from OpenAI API
    """
    deleted_message = client.beta.threads.messages.delete(
        message_id=message_id,
        thread_id=thread_id,
    )
    return deleted_message


def create_run(client, thread_id, assistant_id):
    """
    Create and execute an assistant run on a thread with timeout handling.

    Args:
        client: OpenAI client instance
        thread_id: Thread identifier containing messages to process
        assistant_id: Assistant to execute on the thread

    Returns:
        tuple: (run, run_status, run_response) containing run details
    """
    from ..models import Assistant, ContentItem, Message

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    start_time = time.time()
    time_limit = 60

    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )

        if run_status.status == "completed":
            break

        if time.time() - start_time > time_limit:
            raise TimeoutError("The operation timed out.")

        time.sleep(2)

    message_response = client.beta.threads.messages.list(
        thread_id=thread_id, run_id=run.id
    )

    message_response_id = message_response.data[0].id

    response = client.beta.threads.messages.retrieve(
        message_id=message_response_id,
        thread_id=thread_id,
    )

    data = response.content[0].text.value
    assistant_id = response.assistant_id

    try:
        content_data = json.loads(data)
    except json.JSONDecodeError:
        content_data = data

    if (
        isinstance(content_data, dict)
        and "Content" in content_data
        and "body" in content_data["Content"]
    ):
        content_text = content_data["Content"]["body"]
    else:
        content_text = content_data

    content_detail_id = (
        Message.objects.filter(thread_id=thread_id).first().contentitem.detail_id
    )

    new_content = ContentItem.objects.create(
        assistant_id=assistant_id,
        prompt=Assistant.objects.get(id=assistant_id).instructions,
        content_text=content_text,
        detail_id=content_detail_id,
        content_type="message",
    )

    new_message = Message.objects.create(
        id=message_response_id,
        thread_id=thread_id,
        assistant_id=None,
        status=run_status.status,
        run_id=run.id,
        contentitem_id=new_content.id,
    )

    new_content.save()
    new_message.save()

    run_response = {
        "id": message_response_id,
        "content_text": content_text,
        "assistant_id": assistant_id,
        "status": run_status.status,
        "run_id": run.id,
        "detail_id": content_detail_id,
        "thread_id": thread_id,
    }

    return run, run_status, run_response


def openai_list_messages(client, thread_id):
    """
    Retrieve and format messages from an OpenAI thread.

    Args:
        client: OpenAI client instance
        thread_id: Thread identifier to retrieve messages from

    Returns:
        list: Formatted message list with id, text, and assistant_id
    """
    thread_messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        limit=10,
    )

    formatted_messages = [
        {
            "id": message.id,
            "text": message.content[0].text.value,
            "assistant_id": message.assistant_id,
        }
        for message in thread_messages
    ]
    return formatted_messages

