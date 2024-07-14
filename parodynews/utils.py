# Chat GPT-4o API
# https://platform.openai.com/docs/api-reference/chat-gpt-4o

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os


# Load environment variables from .env file
if load_dotenv():
    print("Environment variables loaded successfully.")
else:
    print("Failed to load environment variables.")

# Get API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print("OPENAI_API_KEY loaded successfully.")
else:
    print("Failed to load OPENAI_API_KEY.")

# Get project ID from environment variables
project_id = os.getenv('PROJECT_ID')
if project_id:
    print("PROJECT_ID loaded successfully.")
else:
    print("Failed to load PROJECT_ID.")

# Get organization ID from environment variables
org_id = os.getenv('ORG_ID')
if org_id:
    print("ORG_ID loaded successfully.")
else:
    print("Failed to load ORG_ID.")


# Use the api_key variable directly instead of os.getenv()
client = OpenAI(
  organization=org_id, # Use the org_id variable
  project=project_id, # Use the project_id variable
  api_key = api_key # Use the api_key variable
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion.choices[0].message.content)

def create_assistant(name, instructions):
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model="gpt-3.5-turbo",
    )
    return assistant

# Function to retrieve assistant information

def retrieve_assistants_info():
    from openai import OpenAI
    client = OpenAI()

    my_assistants = client.beta.assistants.list(
        order="desc",
        limit="20",
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

def generate_content(role, prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
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
    )
    # Get the content of the last message in the response
    return response.choices[0].message.content.strip()


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
        {"id": message.id, "text": message.content[0].text.value} for message in thread_messages
    ]
    return formatted_messages

def delete_thread(thread_id):
    client = OpenAI()

    client.beta.threads.delete(thread_id)

    return f"Thread with ID {thread_id} deleted successfully."