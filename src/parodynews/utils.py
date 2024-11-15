# Chat GPT-4o API
# https://platform.openai.com/docs/api-reference/chat-gpt-4o

from django.db import connection
from .models import AppConfig
from openai import OpenAI

print("Loading utils.py")

# Start up and load the OpenAI API key
def table_exists(table_name):
    db_type = settings.DATABASES['default']['ENGINE']
    
    with connection.cursor() as cursor:
        if 'postgresql' in db_type:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s;", (table_name,))
        elif 'sqlite' in db_type:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        else:
            raise ValueError("Unsupported database type")
        
        return cursor.fetchone() is not None

def get_config_value(key):
    try:
        config = AppConfig.objects.first()  # Assuming only one config is needed
        return getattr(config, key, None)
    except AppConfig.DoesNotExist:
        return None

if table_exists('parodynews_appconfig'):
    api_key = get_config_value('api_key')
    project_id = get_config_value('project_id')
    org_id = get_config_value('org_id')

    if api_key:
        print("OPENAI_API_KEY loaded successfully.")
    else:
        print("Failed to load OPENAI_API_KEY.")

    if project_id:
        print("PROJECT_ID loaded successfully.")
    else:
        print("Failed to load PROJECT_ID.")

    if org_id:
        print("ORG_ID loaded successfully.")
    else:
        print("Failed to load ORG_ID.")
else:
    print("Table 'parodynews_appconfig' does not exist.")

try:
    client = OpenAI(
      organization=org_id,  # Use the org_id variable
      project=project_id,  # Use the project_id variable
      api_key=api_key  # Use the api_key variable
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test, idiot",
            }
        ],
        model="gpt-3.5-turbo",
    )
    print(chat_completion.choices[0].message.content)

except Exception as e:
    print(f"Error: {e}")

# Assistant Creation and Management

def save_assistant(name, description, instructions, model, json_schema, assistant_id=None):
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
            model=model,
            response_format=response_format
        )
    else:
        assistant = client.beta.assistants.create(
            name=name,
            description=description,
            instructions=instructions,
            model=model,
            response_format=response_format
        )
    
    return assistant

def get_assistant(assistant_id):
    assistant = client.beta.assistants.retrieve(assistant_id)
    return assistant

# Function to retrieve assistant information

def retrieve_assistants_info():
    client = OpenAI()

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

def openai_delete_assistant(assistant_id):
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



def generate_content(content_form):

    model = content_form.assistant.model

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

    content_detail = generate_content_detail(data)

    # Log the response
    logging.info("Response: %s", data, content_detail)
    
    return data, content_detail

# Load all schemas and store them in a variable
all_schemas = load_schemas()

parody_schema = resolve_refs(all_schemas.get('parody_news_article_schema'))
content_detail_schema = resolve_refs(all_schemas.get('content_detail_schema'))

def generate_content_detail(content):
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
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
    logging.info("Response: %s", data)
    
    return content_detail


def openai_create_message(content):
    thread = client.beta.threads.create(
        metadata={"type": "news_article_thread",
                  "title": content.detail.title,
                  "description": content.detail.description,},
    )
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content.content
    )
    return message, thread.id

def openai_delete_message(message_id, thread_id):
    deleted_message = client.beta.threads.messages.delete(
    message_id=message_id,
    thread_id=thread_id,
    )
    return deleted_message

def create_run(thread_id, assistant_id):
    import time

    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    )

    
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        
        if run_status.status == "completed":
            break
        time.sleep(2)

    new_message = client.beta.threads.messages.list(
        thread_id=thread_id,
        run_id=run.id
        )

    new_message_id = new_message.data[0].id

    # https://platform.openai.com/docs/api-reference/messages/getMessage
    response = client.beta.threads.messages.retrieve(
    message_id=new_message_id,
    thread_id=thread_id,
    )

    data = response.content[0].text.value
    assistant_id = response.assistant_id

    try:
        content_data = json.loads(data)
    except json.JSONDecodeError:
        content_data = data
    
    if isinstance(content_data, dict) and 'Content' in content_data and 'body' in content_data['Content']:
        content_section = content_data['Content']['body']
    else:
        content_section = content_data

    message_data = {"id": new_message_id,
                    "content": content_section,
                    "assistant_id": assistant_id,
                }

    return run, run_status, message_data


def openai_list_messages(thread_id):
    client = OpenAI()

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



def generate_content_detail(content):

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

