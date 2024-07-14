from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed

from .forms import ContentForm, AssistantForm
from .models import Content, ContentDetail, Message, Assistant, Thread
from . import utils  # Import the utils module
from .utils import (
    delete_assistant,
    generate_content, 
    retrieve_assistants_info,
    create_assistant
)
from .scripts.create_jekyll_post import create_jekyll_post
from openai import OpenAI  # Import OpenAI library
from datetime import datetime

def index(request):
    # This view will render the root index page
    return render(request, 'parodynews/index.html', {})

# Ensure the rest of your views.py file remains unchanged

from django.shortcuts import render, redirect
from .forms import ContentForm  # Assuming ContentForm is your form for creating content
from .models import Content, ContentDetail  # Assuming these are your models
from .utils import generate_content  # Assuming this is your function to generate content

def manage_content(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            # Create and save ContentDetail instance
            title = form.cleaned_data.get('title', 'Default Title')
            description = form.cleaned_data.get('description', 'Default Description')
            author = form.cleaned_data.get('author', 'Default Author')
            content_detail = ContentDetail(title=title, description=description, author=author)
            content_detail.save()

            # Generate content based on the form's role and prompt
            role = form.cleaned_data['role']
            prompt = form.cleaned_data['prompt']
            generated_content = generate_content(role, prompt)

            # Create and save Content instance, linking it to the ContentDetail instance
            post = form.save(commit=False)
            post.content = generated_content
            post.detail = content_detail  # Link to the ContentDetail instance
            post.save()

            # Redirect to prevent form resubmission
            return redirect('manage_content')  # Adjust the redirect as needed

    else:
        form = ContentForm()

    # This part is executed for both POST (after redirecting) and GET requests
    generated_content_list = Content.objects.all()  # Retrieve all content from the database
    messages.success(request, "Content created successfully.")
    # Render the template with the context
    return render(request, 'parodynews/content_detail.html', {
        'form': form,
        'generated_content': generated_content_list
    })
# New view function to create an assistant


def manage_assistants(request):
    if request.method == 'POST':
        form = AssistantForm(request.POST)
        if form.is_valid():
            assistant_name = form.cleaned_data['assistant_name']
            instructions = form.cleaned_data['instructions']
            
            # Create an assistant using your custom function
            assistant = create_assistant(assistant_name, instructions)
            
            # Initialize the OpenAI client
            client = OpenAI()
            
            # Retrieve the assistant details from OpenAI using the assistant ID
            assistant_id = assistant.id
            my_assistant = client.beta.assistants.retrieve(assistant_id)
            
            # Save the assistant details to the database
            db_assistant = Assistant(
                assistant_id=assistant_id,
                name=assistant_name,
                model=my_assistant.model,
                created_at=datetime.fromtimestamp(my_assistant.created_at)
            )
            db_assistant.save()
            messages.success(request, "Assistant created successfully.")
            
            # Redirect to the same page or a confirmation page to prevent form resubmission
            return redirect('manage_assistants')  # Replace 'manage_assistants' with the name of your view or URL pattern

    # This part is executed for GET requests and after redirecting
    form = AssistantForm()  # Always provide a fresh form for new entries
    assistants_info = retrieve_assistants_info()  # Retrieve the list of assistants for the context
    
    # Render the template with the context
    return render(request, 'parodynews/assistant_detail.html', {
        'form': form,
        'assistants_info': assistants_info
    })


def delete_assistant(request, assistant_id):
    # Call the delete function from utils.py
    response_message = utils.delete_assistant(assistant_id)
    # Optionally, add a success message
    messages.success(request, response_message)
    # Redirect to the list of assistants or another appropriate page
    return redirect('manage_assistants')



@require_POST
def create_message(request):
    content_id = request.POST.get('content_id')
    try:
        content = Content.objects.get(id=content_id)
    except Content.DoesNotExist:
        return HttpResponseBadRequest("The requested content does not exist.")

    # Call utils.create_message to get message and thread_id
    message, thread_id = utils.create_message(content.content)
    
    # Create a new Thread instance and save it
    new_thread = Thread(thread_id=thread_id)  # Assuming Thread model doesn't require any mandatory fields
    new_thread.save()

    print(f"New thread created with ID: {content_id}")

    # Create and save the new Message instance with the thread_id
    new_message = Message(message_id=message.id, content_id=content_id, thread_id=new_thread.thread_id)
    new_message.save()

    messages.success(request, "Message created successfully.")
    return redirect('list_messages')

def delete_message(request, message_id):
    # Retrieve the message instance
    try:
        message = Message.objects.get(message_id=message_id)
    except Message.DoesNotExist:
        return HttpResponseBadRequest("The requested message does not exist.")
    
    # Delete the message
    message.delete()

    messages.success(request, "Message deleted successfully.")
    return redirect('list_messages')


def list_messages(request):
    # Check if the request method is GET
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response if not a GET request
        return HttpResponseNotAllowed(['GET'])
    
    # Retrieve all messages from the database
    message_list = Message.objects.all()
    assistants = Assistant.objects.all()  # Fetch all assistants

    # Render the list of messages with the 'list_messages.html' template
    return render(request, 'parodynews/message_detail.html', {'message_list': message_list, 'assistants': assistants})

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import Message, Assistant

def assign_assistant_to_message(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(Message, pk=message_id)
        assistant_id = request.POST.get('assistant_id')
        assistant = get_object_or_404(Assistant, pk=assistant_id)
        message.assistant_id = assistant  # Assuming your Message model has a ForeignKey to Assistant
        message.save()
        return redirect('list_messages')  # Redirect to the messages list page or wherever appropriate
    else:
        return HttpResponse("Method not allowed", status=405)
    
from django.http import HttpResponse, HttpResponseRedirect
from .utils import create_run
from django.urls import reverse

def run_messages(request, message_id):
    from .models import Message  # Import the Message model

    if request.method == "POST":
        try:
            message = Message.objects.get(message_id=message_id)  # Retrieve the message by its ID
            thread_id = message.thread_id  # Access the thread_id associated with the message
            assistant_id = request.POST.get('assistant_id')  # Assuming assistant_id is passed in the request
            create_run(thread_id, assistant_id)  # Pass thread_id instead of message_id
            return redirect('list_messages')
        except Message.DoesNotExist:
            return HttpResponse("Message not found", status=404)
    else:
        return HttpResponse("Invalid request", status=400)
    
from django.shortcuts import render, get_object_or_404
from .models import Thread  # Assuming you have a Thread model
from .utils import openai_list_messages

def thread_detail(request, thread_id=None):
    threads = Thread.objects.all()  # Retrieve all threads
    thread_messages = []
    thread = None

    if thread_id:
        thread = get_object_or_404(Thread, pk=thread_id)
        thread_messages = openai_list_messages(thread_id)

    return render(request, 'parodynews/thread_detail.html', {'threads': threads, 'current_thread': thread, 'thread_messages': thread_messages})

from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Thread  # Adjust the import path according to your project structure

@require_POST
def delete_thread(request, thread_id):
    # Fetch the thread from the database or return a 404 error if not found
    thread = get_object_or_404(Thread, pk=thread_id)
    # Delete the thread
    thread.delete()
    # Redirect to a suitable page after deletion, e.g., the threads list page
    return redirect('thread_detail')  # Replace 'threads_list' with the name of your threads list view