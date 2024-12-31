# Chat GPT-4o API
# https://platform.openai.com/docs/api-reference/chat-gpt-4o

from django.db import connection
from .models import AppConfig, Assistant, ContentItem, Message
from openai import OpenAI
from django.conf import settings

print("Loading utils.py")

# Start up and load the OpenAI API key
from django.apps import apps

from django.db.models import Q

def table_exists_and_fields_populated(model_name):
    try:
        model = apps.get_model('parodynews', model_name)
        if model.objects.exists():
            return model.objects.filter(
                Q(api_key__isnull=False) & ~Q(api_key='') &
                Q(project_id__isnull=False) & ~Q(project_id='') &
                Q(org_id__isnull=False) & ~Q(org_id='')
            ).exists()
        return False
    except LookupError:
        return False
    pass

def get_config_value(key):
    try:
        config = AppConfig.objects.first()  # Assuming only one config is needed
        return getattr(config, key, None)
    except AppConfig.DoesNotExist:
        return None
    pass

def load_openai_client(client):
    return client

def save_assistant(client, name, description, instructions, model, json_schema, assistant_id=None):
    if json_schema is not None:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": json_schema.name,
                "description": json_schema.description,
                "schema": json_schema.schema,
                "strict": True,
            }
        }

    else:
        response_format = None

    if assistant_id:
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            name=name,
            instructions=instructions,
            model=model.model_id,
            response_format=response_format
        )
    else:
        assistant = client.beta.assistants.create(
            name=name,
            description=description,
            instructions=instructions,
            model=model.model_id,
            response_format=response_format
        )
    
    return assistant

def get_assistant(client, assistant_id):
    assistant = client.beta.assistants.retrieve(assistant_id)
    return assistant

# Function to retrieve assistant information

def retrieve_assistants_info(client):
    my_assistants = client.beta.assistants.list(
        order="desc",
        limit="100",
    )

    assistants_info = [{
        "id": assistant.id,
        "name": assistant.name,
        "instructions": assistant.instructions
    } for assistant in my_assistants.data]

    return assistants_info

# Function to delete an assistant

def openai_delete_assistant(client, assistant_id):
    # Assuming you have a Django model named Assistant

    client.beta.assistants.delete(assistant_id)

    return f"Assistant with ID {assistant_id} deleted successfully."

# Function to generate content

import logging

# Configure logging
logging.basicConfig(
    filename='assistant_responses.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
import json
import jsonref
import os

def load_schemas():
    # Define the path to the schema directory
    schema_dir = os.path.join(os.path.dirname(__file__), 'schema')
    
    # Dictionary to hold all loaded schemas
    schemas = {}

    try:
        # Iterate over all files in the schema directory
        for filename in os.listdir(schema_dir):
            if filename.endswith('.json'):
                # Construct the full file path
                json_file_path = os.path.join(schema_dir, filename)
                
                # Read and parse the JSON file with reference resolution
                with open(json_file_path, 'r') as file:
                    base_uri = f'file://{schema_dir}/'
                    schema = jsonref.load(file, base_uri=base_uri, jsonschema=True)
                    # Add the schema to the dictionary
                    schemas[os.path.splitext(filename)[0]] = schema
    except FileNotFoundError:
        print(f"Error: The directory {schema_dir} was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from a file in {schema_dir}. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while reading files in {schema_dir}. Error: {e}")

    # Optionally, you can add a check to ensure at least one schema was loaded correctly
    if schemas:
        print("JSON schemas loaded successfully with references resolved.")
    else:
        print("Failed to load JSON schemas.")

    return schemas

def resolve_refs(obj):
    if isinstance(obj, jsonref.JsonRef):
        # If it's a JsonRef object, resolve it
        return resolve_refs(obj.__subject__)
    elif isinstance(obj, dict):
        # Recursively apply to dictionary values
        return {k: resolve_refs(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Recursively apply to list items
        return [resolve_refs(i) for i in obj]
    else:
        # Return the object as is if it's not a reference or collection
        return obj

def generate_content(client, content_form):

    model = content_form.assistant.model.model_id

    if content_form.assistant.json_schema is not None:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "News_Article",
                "description": "A JSON object representing a news article.",
                "schema": content_form.assistant.json_schema.schema,
                "strict": True,
            }
        }

    else:
        response_format = None

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": content_form.assistant.instructions,
                    },
                ],
            },
            {
                "role": "user",
                "content": content_form.prompt,
            }
        ],
        response_format=response_format
    )
    # Get the content of the last message in the response
    data = response.choices[0].message.content

    content_detail = generate_content_detail(client, data)

    # Log the response
    logging.info("Response: %s", data, content_detail)
    
    return data, content_detail

# Load all schemas and store them in a variable
all_schemas = load_schemas()

parody_schema = resolve_refs(all_schemas.get('parody_news_article_schema'))
content_detail_schema = resolve_refs(all_schemas.get('content_detail_schema'))

def generate_content_detail(client, content):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "generate content detail",
                    },
                ],
            },
            {
                "role": "user",
                "content": content,
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Metadata",
                "description": "A JSON object representing details of a news article.",
                "schema": content_detail_schema,
                "strict": True,
           }
        }
    )
    # Get the content of the last message in the response
    content_detail = response.choices[0].message.content
    
    # Log the response
    logging.info("Response: %s", content_detail)
    
    return content_detail

def openai_create_message(client, contentitem):
    thread = client.beta.threads.create(
        metadata={"type": "news_article_thread",
                  "title": contentitem.detail.title,
                  "description": contentitem.detail.description,},
    )
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=contentitem.content_text
    )
    return message, thread.id

def openai_delete_message(client, message_id, thread_id):
    deleted_message = client.beta.threads.messages.delete(
    message_id=message_id,
    thread_id=thread_id,
    )
    return deleted_message


def create_run(client, thread_id, assistant_id):
    import time
    # https://platform.openai.com/docs/api-reference/runs/createRun

    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    )

    start_time = time.time()
    time_limit = 60  # Time limit in seconds

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
        thread_id=thread_id,
        run_id=run.id
        )

    message_response_id = message_response.data[0].id

    # https://platform.openai.com/docs/api-reference/messages/getMessage
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
    
    if isinstance(content_data, dict) and 'Content' in content_data and 'body' in content_data['Content']:
        content_text = content_data['Content']['body']
    else:
        content_text = content_data

    # retrieve the content item detail from the thread id
    
    content_detail_id = Message.objects.filter(thread_id=thread_id).first().contentitem.detail_id

    # Create a new content item instance with the response content
    new_content = ContentItem.objects.create(
        assistant_id=assistant_id,
        prompt=Assistant.objects.get(id=assistant_id).instructions,
        content_text=content_text,
        detail_id=content_detail_id,
        content_type='message'
    )

    # Create a new message instance with the response content
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

    run_response = {"id": message_response_id,
                    "content_text": content_text,
                    "assistant_id": assistant_id,
                    "status": run_status.status,
                    "run_id": run.id,
                    "detail_id": content_detail_id,
                    "thread_id": thread_id
                }

    # Return the run, run_status, and message_data
    return run, run_status, run_response

def openai_list_messages(client, thread_id):
    thread_messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        limit=10,
    )
    # Assuming each message in thread_messages has a 'content' attribute
    formatted_messages = [
        {"id": message.id, "text": message.content[0].text.value, "assistant_id": message.assistant_id} for message in thread_messages
    ]
    return formatted_messages

# Function to convert JSON to Markdown

def json_to_markdown(data):
    # Function to convert JSON object to Markdown recursively
    def convert_to_md(data, level=1):
        markdown = ""
        if isinstance(data, dict):
            for key, value in data.items():
                markdown += f"{'#' * level} {key}\n\n"
                markdown += convert_to_md(value, level + 1)
        elif isinstance(data, list):
            for item in data:
                markdown += f"* {convert_to_md(item, level + 1)}\n"
        else:
            markdown += f"{data}\n\n"
        return markdown

    return convert_to_md(data)

from django.conf import settings

def generate_markdown_file(data, filename):
    """
    Generates a markdown (.md) file from the provided data.
    
    :param data: The data to be written to the markdown file.
    :param filename: The name of the markdown file to be generated.
    :return: The path to the generated markdown file.
    """

    # Define the file path
    file_path = os.path.join(settings.POST_DIR, filename)

    # Write the markdown content to the file
    with open(file_path, 'w') as file:
        file.write(data)
    
    return file_path

def generate_content_detail(client, content):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "generate content detail",
                    },
                ],
            },
            {
                "role": "user",
                "content": content,
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Metadata",
                "description": "A JSON object representing details of a news article.",
                "schema": content_detail_schema,
                "strict": True,
           }
        }
    )
    # Get the content of the last message in the response
    data = response.choices[0].message.content
    
    # Log the response
    logging.info("Response: %s", data)
    
    return data

def create_or_update_assistant(client, validated_data):
    name = validated_data.get('name')
    description = validated_data.get('description')
    instructions = validated_data.get('instructions', 'you are a helpful assistant.')
    model = validated_data.get('model')
    json_schema = validated_data.get('json_schema')
    assistant_id = validated_data.get('id', None)  # For updates

    # Create or update the assistant in OpenAI
    assistant_ai = save_assistant(
        client,
        name,
        description,
        instructions,
        model,
        json_schema,
        assistant_id
    )

    # Update or create the Assistant object in the database
    assistant, created = Assistant.objects.update_or_create(
        id=assistant_ai.id,
        defaults={
            'name': name,
            'description': description,
            'instructions': instructions,
            'model': model,
            'json_schema': json_schema,
        }
    )
    return assistant

def get_openai_client():
    import openai
    api_key = get_config_value('api_key')
    org_id = get_config_value('org_id')

    openai.api_key = api_key
    if (org_id):
        openai.organization = org_id

    return openai

def delete_assistant(client, assistant_id):
    # Delete assistant from OpenAI API
    client.beta.assistants.delete(assistant_id)
    # Delete assistant from the database
    Assistant.objects.filter(id=assistant_id).delete()
    return f"Assistant with ID {assistant_id} deleted successfully."

def run_assistant(assistant, input_content):
    client = get_openai_client()
    response = client.chat_completion.create(
        model=assistant.model.model_id,
        messages=[
            {"role": "system", "content": assistant.instructions},
            {"role": "user", "content": input_content}
        ],
        temperature=assistant.temperature or 0.7
    )
    output_content = response.choices[0].message.content
    return output_content

def generate_unique_id():
    import uuid
    return str(uuid.uuid4())