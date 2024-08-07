# Chat GPT-4o API
# https://platform.openai.com/docs/api-reference/chat-gpt-4o

from .models import AppConfig
from openai import OpenAI
# utils.py (modified usage example)

# Start up and load the OpenAI API key
def get_config_value(key):
    try:
        config = AppConfig.objects.first()  # Assuming only one config is needed
        return getattr(config, key, None)
    except AppConfig.DoesNotExist:
        return None

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

def create_assistant(name, description, instructions, model):
    assistant = client.beta.assistants.create(
        name=name,
        description=description,
        instructions=instructions,
        model=model,
    )
    return assistant

def update_assistant(assistant_id, name, instructions, model):
    assistant = client.beta.assistants.update(
        assistant_id,
        name=name,
        instructions=instructions,
        model=model,
    )
    return assistant

# Core Assistant Functions

## Meta Data 

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

def delete_assistant(assistant_id):
    # Assuming you have a Django model named Assistant
    from .models import Assistant
    Assistant.objects.filter(assistant_id=assistant_id).delete()
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
import os

# Define the path to the JSON file
json_file_path = os.path.join(os.path.dirname(__file__), 'schema/parody_news_article_schema.json')

# Read and parse the JSON file
with open(json_file_path, 'r') as file:
    news_article_schema = json.load(file)

def generate_content(role, prompt):
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": role,
                    },
                ],
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "News_Article",
                "description": "A JSON object representing a news article.",
                "schema": news_article_schema,
                "strict": True,
           }
        }
    )
    # Get the content of the last message in the response
    data = response.choices[0].message.content.strip()
    
    # Log the response
    logging.info("Response: %s", data)
    
    return data

def create_message(content):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )
    return message, thread.id

def create_run(thread_id, assistant_id):
    client = OpenAI()

    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    )
    return run

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



def delete_thread(thread_id):
    client = OpenAI()

    client.beta.threads.delete(thread_id)

    return f"Thread with ID {thread_id} deleted successfully."

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


import os
from django.conf import settings
from .models import ContentDetail

def generate_markdown_file(data, filename):
    """
    Generates a markdown (.md) file from the provided data.
    
    :param data: The data to be written to the markdown file.
    :param filename: The name of the markdown file to be generated.
    :return: The path to the generated markdown file.
    """
    # Fetch the published_at field from the ContentDetail model
    content_detail = ContentDetail.objects.get(title=filename)
    published_at = content_detail.published_at

    # Format the date and title for the filename
    date_str = published_at.strftime("%Y-%m-%d")
    formatted_filename = f"{date_str}-{filename}.md"

    # Define the file path
    file_path = os.path.join(settings.POST_DIR, formatted_filename)

    # Write the markdown content to the file
    with open(file_path, 'w') as file:
        file.write(data)
    
    return file_path