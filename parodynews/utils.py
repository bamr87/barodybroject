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
        model="gpt-4o",
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


