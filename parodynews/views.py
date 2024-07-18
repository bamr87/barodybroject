from datetime import datetime
from django import utils
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from datetime import timezone, datetime
from .forms import AssistantForm, ContentForm, RoleForm
from .models import Assistant, Content, ContentDetail, Message, SystemRole, Thread
from .utils import (
    create_assistant, 
    create_run, 
    delete_assistant, 
    generate_content, 
    openai_list_messages, 
    retrieve_assistants_info
)
from .scripts.create_jekyll_post import create_jekyll_post
from openai import OpenAI  # Import OpenAI library if directly used, otherwise remove


def index(request):
    # This view will render the root index page
    return render(request, 'parodynews/index.html', {})

def manage_content(request):
    from django.db import DatabaseError

    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            try:
                # Create and save ContentDetail instance
                title = form.cleaned_data.get('title', 'Default Title')
                description = form.cleaned_data.get('description', 'Default Description')
                author = form.cleaned_data.get('author', 'Default Author')
                content_detail = ContentDetail(title=title, description=description, author=author)
                content_detail.save()

                # Generate content based on the form's role and prompt
                instructions = form.cleaned_data['instructions']
                prompt = form.cleaned_data['prompt']
                try:
                    generated_content = generate_content(instructions, prompt)
                except Exception as e:
                    messages.error(request, f"Failed to generate content: {e}")
                    return render(request, 'parodynews/content_detail.html', {'form': form})

                # Create and save Content instance, linking it to the ContentDetail instance
                content = form.save(commit=False)
                content.content = generated_content
                # Assuming you have a way to determine the system_role, e.g., from the request
                system_role = request.POST.get('system_role')
                system_role = SystemRole.objects.get(id=system_role)
                content.system_role = system_role
                content.detail = content_detail  # Link to the ContentDetail instance
                content.save()

                messages.success(request, "Content created successfully.")
                return redirect('manage_content')
            except DatabaseError as e:
                messages.error(request, f"Database error: {e}")
                return render(request, 'parodynews/content_detail.html', {'form': form})
        else:
            # If form is not valid, add an error message and include form errors
            error_messages = form.errors.as_text()
            messages.error(request, f"Form validation failed: {error_messages}")
            # No need to redirect, just render the same page with the form containing errors
            return render(request, 'parodynews/content_detail.html', {'form': form})
    else:
        form = ContentForm()

    # This part is executed for both POST (after redirecting) and GET requests
    generated_content_list = Content.objects.all()
    return render(request, 'parodynews/content_detail.html', {
        'form': form,
        'generated_content': generated_content_list
    })

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
            
            # Assuming there's a ForeignKey from Assistant to SystemRole in your models
            # Update the SystemRole creation to include the link

            # Retrieve the assistant details from OpenAI using the assistant ID
            assistant_id = assistant.id
            my_assistant = client.beta.assistants.retrieve(assistant_id)

            # First, create or update the SystemRole with the assistant_name
            system_role, created = SystemRole.objects.get_or_create(
                role_name=assistant_name,
                instructions=instructions,
                role_type=SystemRole.ASSISTANT
            )

            # Now, save the assistant details to the database with a link to the SystemRole
            db_assistant = Assistant(
                assistant_id=assistant_id,
                description=instructions,
                model=my_assistant.model,
                created_at=datetime.fromtimestamp(my_assistant.created_at),
                system_role=system_role  # Link the Assistant instance to the SystemRole instance
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
    

def run_messages(request, message_id):
    from .models import Message  # Import the Message model

    if request.method == "POST":
        message = get_object_or_404(Message, message_id=message_id)  # Retrieve the message by its ID or return 404
        thread_id = message.thread_id  # Access the thread_id associated with the message
        assistant_id = request.POST.get('assistant_id')  # Assuming assistant_id is passed in the request
        create_run(thread_id, assistant_id)  # Pass thread_id instead of message_id
        
        # Redirect to the thread_detail.html of the message
        return redirect('thread_detail', thread_id=thread_id)
    else:
        return HttpResponse("Invalid request", status=400)


def thread_detail(request, thread_id=None):
    threads = Thread.objects.all()  # Retrieve all threads
    thread_messages = []
    current_thread = None

    if thread_id:
        current_thread = get_object_or_404(Thread, pk=thread_id)
        thread_messages = openai_list_messages(thread_id)

    return render(request, 'parodynews/thread_detail.html', {'threads': threads, 'current_thread': current_thread, 'thread_messages': thread_messages})


@require_POST
def delete_thread(request, thread_id):
    # Fetch the thread from the database or return a 404 error if not found
    thread = get_object_or_404(Thread, pk=thread_id)
    # Delete the thread
    thread.delete()
    # Redirect to a suitable page after deletion, e.g., the threads list page
    return redirect('thread_detail')  # Replace 'threads_list' with the name of your threads list view



@require_POST
def add_message_to_db(request):
    message_id = request.POST.get('message_id')
    message_content = request.POST.get('message_content')
    thread_id = request.POST.get('thread_id')
    assistant_id = request.POST.get('assistant_id')

    # First, create the ContentDetail object
    content_detail = ContentDetail.objects.create(
        title="Generated Title",  # Placeholder title, adjust as needed
        description="Generated Description",  # Placeholder description, adjust as needed
        author="Generated Author",  # Placeholder author, adjust as needed
        published_at=datetime.now(),  # Use the current time for published_at
    )
    # Retrieve the ContentDetail instance using the ID
    content_detail_instance = ContentDetail.objects.get(id=content_detail.id)

    # Then, create or update the Content object with the content_detail instance
    content, _ = Content.objects.update_or_create(
        prompt= Assistant.objects.get(assistant_id=assistant_id).system_role.instructions,  # Assuming you want to use the message_content as the prompt
        system_role= Assistant.objects.get(assistant_id=assistant_id).system_role,  # Assuming you want to use the message_content as the prompt
        content=message_content,
        detail=content_detail_instance  # Use the ContentDetail instance here
    )

    # Update content_detail to link to the newly created or updated content
    content_detail.content = content
    content_detail.save()

    # Create or update the Message object
    message = Message.objects.update_or_create(
        message_id=message_id,
        thread_id=thread_id,
        defaults={'content': content, 'created_at': datetime.now()}
    )
    messages.success(request, "Message and content created successfully.")

    return redirect('thread_detail')  # Redirect back to the thread detail page


def manage_roles(request):
    # Initialize an empty form for the creation of a new role
    create_form = RoleForm()
    form = None  # This will be used for modifications

    if request.method == 'POST':
        if 'create' in request.POST:
            create_form = RoleForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                return redirect('manage_roles')  # Redirect to clear the form
        elif 'modify' in request.POST:
            role_id = request.POST.get('role_id')
            role = SystemRole.objects.get(pk=role_id)
            form = RoleForm(request.POST, instance=role)
            if form.is_valid():
                form.save()
        elif 'delete' in request.POST:
            role_id = request.POST.get('role_id')
            role = SystemRole.objects.get(pk=role_id)
            role.delete()
        # Redirect after modify or delete to prevent re-posting
        return redirect('manage_roles')
    else:
        roles = SystemRole.objects.all()
        # Pass both the create_form and form for modification
        # If no role is being modified, 'form' remains None
        return render(request, 'parodynews/role_detail.html', {'roles': roles, 'form': form, 'create_form': create_form})
    

def get_role_instructions(request):
    role_id = request.GET.get('role_id')
    instructions = ''
    system_role = ''  # Initialize system_role variable
    if role_id:
        try:
            role = SystemRole.objects.get(id=role_id)
            instructions = role.instructions
            system_role = role.id  # Assuming you want to return the role's ID as the system_role value
            # If you have a specific field for system_role, replace role.id with role.<field_name>
        except SystemRole.DoesNotExist:
            instructions = 'Role not found.'
            system_role = None  # Set system_role to None or an appropriate value if the role does not exist
    return JsonResponse({'instructions': instructions, 'system_role': system_role})