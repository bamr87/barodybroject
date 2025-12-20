"""
File: assistants.py
Description: Assistant management helpers for OpenAI API integration
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- openai: >=1.57.0

Usage: from parodynews.utils.assistants import save_assistant
"""

from .config import get_openai_client


def save_assistant(
    client, name, description, instructions, model, json_schema, assistant_id=None
):
    """
    Create or update an OpenAI assistant with JSON schema support.

    Args:
        client: OpenAI client instance
        name: Display name for the assistant
        description: Description of assistant capabilities
        instructions: System instructions for assistant behavior
        model: Model instance with model_id attribute
        json_schema: JSONSchema instance or None for unstructured output
        assistant_id: Existing assistant ID for updates (optional)

    Returns:
        OpenAI assistant object with configured parameters
    """
    if json_schema is not None:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": json_schema.name,
                "description": json_schema.description,
                "schema": json_schema.schema,
                "strict": True,
            },
        }
    else:
        response_format = None

    if assistant_id:
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            name=name,
            instructions=instructions,
            model=model.model_id,
            response_format=response_format,
        )
    else:
        assistant = client.beta.assistants.create(
            name=name,
            description=description,
            instructions=instructions,
            model=model.model_id,
            response_format=response_format,
        )

    return assistant


def get_assistant(client, assistant_id):
    """
    Retrieve an OpenAI assistant by ID.

    Args:
        client: OpenAI client instance
        assistant_id: Unique identifier for the assistant

    Returns:
        OpenAI assistant object with full configuration
    """
    assistant = client.beta.assistants.retrieve(assistant_id)
    return assistant


def retrieve_assistants_info(client):
    """
    Retrieve summary information for all user assistants.

    Args:
        client: OpenAI client instance

    Returns:
        List of dictionaries containing assistant id, name, and instructions
    """
    my_assistants = client.beta.assistants.list(
        order="desc",
        limit="100",
    )

    assistants_info = [
        {
            "id": assistant.id,
            "name": assistant.name,
            "instructions": assistant.instructions,
        }
        for assistant in my_assistants.data
    ]

    return assistants_info


def openai_delete_assistant(client, assistant_id):
    """
    Delete an OpenAI assistant by ID.

    Args:
        client: OpenAI client instance
        assistant_id: Unique identifier of assistant to delete

    Returns:
        str: Deletion confirmation message
    """
    client.beta.assistants.delete(assistant_id)
    return f"Assistant with ID {assistant_id} deleted successfully."


def create_or_update_assistant(client, validated_data):
    """
    Create or update an OpenAI assistant with database synchronization.

    Args:
        client: OpenAI client instance
        validated_data: Dictionary containing assistant configuration

    Returns:
        Assistant Django model instance
    """
    from ..models import Assistant

    name = validated_data.get("name")
    description = validated_data.get("description")
    instructions = validated_data.get("instructions", "you are a helpful assistant.")
    model = validated_data.get("model")
    json_schema = validated_data.get("json_schema")
    assistant_id = validated_data.get("id", None)

    assistant_ai = save_assistant(
        client, name, description, instructions, model, json_schema, assistant_id
    )

    assistant, created = Assistant.objects.update_or_create(
        id=assistant_ai.id,
        defaults={
            "name": name,
            "description": description,
            "instructions": instructions,
            "model": model,
            "json_schema": json_schema,
        },
    )
    return assistant


def delete_assistant(client, assistant_id):
    """
    Delete an assistant from both OpenAI API and local database.

    Args:
        client: OpenAI client instance
        assistant_id: Unique identifier of assistant to delete

    Returns:
        str: Deletion confirmation message
    """
    from ..models import Assistant

    client.beta.assistants.delete(assistant_id)
    Assistant.objects.filter(id=assistant_id).delete()
    return f"Assistant with ID {assistant_id} deleted successfully."


def run_assistant(assistant, input_content):
    """
    Execute an assistant with legacy chat completion interface.

    Args:
        assistant: Assistant model instance
        input_content: User message content to process

    Returns:
        str: Generated response content from the assistant
    """
    client = get_openai_client()
    response = client.chat_completion.create(
        model=assistant.model.model_id,
        messages=[
            {"role": "system", "content": assistant.instructions},
            {"role": "user", "content": input_content},
        ],
        temperature=assistant.temperature or 0.7,
    )
    output_content = response.choices[0].message.content
    return output_content

