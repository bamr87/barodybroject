# Chat GPT-4o API
# https://platform.openai.com/docs/api-reference/chat-gpt-4o

from .models import AppConfig
from openai import OpenAI

# utils.py (modified usage example)

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


def create_assistant(name, description, instructions, model):
    assistant = client.beta.assistants.create(
        name=name,
        description=description,
        instructions=instructions,
        model=model,
    )
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
            },
            {
                "role": "assistant",
                "content": "output the title, description, and content in a json format.",
            }
        ],
        response_format={
            "type": "json_object",
        }
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
        {"id": message.id, "text": message.content[0].text.value, "assistant_id": message.assistant_id} for message in thread_messages
    ]
    return formatted_messages



def delete_thread(thread_id):
    client = OpenAI()

    client.beta.threads.delete(thread_id)

    return f"Thread with ID {thread_id} deleted successfully."

# Function to convert JSON to Markdown
def json_to_markdown(data, level=1):
    markdown_text = ""
    
    if isinstance(data, dict):
        for key, value in data.items():
            # Add the heading
            markdown_text += f"{'#' * level} {key.replace('_', ' ').title()}\n\n"
            # Recursively add the content
            markdown_text += json_to_markdown(value, level + 1)
    elif isinstance(data, list):
        for item in data:
            # Process each list item without adding extra headings
            item_text = json_to_markdown(item, level)
            # Ensure list items are properly formatted
            markdown_text += f"{item_text.strip()}\n"
    else:
        # Add the content
        markdown_text += f"{data}\n\n"
    
    return markdown_text