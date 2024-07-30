import json
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django import utils
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views import View
from django.db import DatabaseError
from datetime import timezone, datetime
from .forms import AssistantForm, ContentForm
from .models import Assistant, Content, ContentDetail, Message, Thread
from .utils import (
    create_assistant, 
    create_run, 
    delete_assistant, 
    generate_content, 
    openai_list_messages, 
    retrieve_assistants_info,
    create_message,
    json_to_markdown
)
from openai import OpenAI

# Custom LoginView to render a custom login page
class UserLoginView(LoginView):
    template_name = 'login.html'

# View to render the index page
def index(request):
    # This view will render the root index page
    return render(request, 'parodynews/index.html', {})

# View to manage content creation and deletion
class ManageContentView(LoginRequiredMixin, View):
    def get(self, request, content_id=None):
        form = ContentForm()
        selected_content = None
        if content_id:
            selected_content = get_object_or_404(Content, id=content_id)

        generated_content = Content.objects.all()

        # Create a list to hold content and their details
        content_with_details = []
        for content in generated_content:
            content_detail = ContentDetail.objects.filter(id=content.detail_id).first()
            content_with_details.append({
                'content': content,
                'content_detail': content_detail
            })
        
        return render(request, 'parodynews/content_detail.html', {
            'form': form,
            'selected_content': selected_content,
            'generated_content': generated_content,
            'content_with_details': content_with_details
        })

    def post(self, request):
        if request.POST.get('_method') == 'delete':
            return self.delete(request)
        
        form = ContentForm(request.POST)
        if form.is_valid():


            # Generate content based on the form's role and prompt
            instructions = form.cleaned_data['instructions']
            prompt = form.cleaned_data['prompt']

            generated_content_response = generate_content(instructions, prompt)
            generated_content = json.loads(generated_content_response)

            title = generated_content.get('title', 'Default Title')
            description = generated_content.get('description', 'Default Description')
            
            author = form.cleaned_data.get('author', 'Default Author')
            content_detail = ContentDetail(title=title, description=description, author=author)
            content_detail.save()
            
            content_text = json_to_markdown(generated_content.get('content'))

            if content_text == "None":
                content_text = json_to_markdown(generated_content_response)
            
            content = form.save(commit=False)
            content.content = content_text
            content.detail_id = content_detail.id  # Set the detail_id field

            assistant = request.POST.get('assistant')
            assistant = Assistant.objects.get(assistant_id=assistant)
            content.assistant = assistant
            content.save()


            messages.success(request, "Content created successfully!")
            return redirect('content_detail', content_id=content.id)

        generated_content = Content.objects.all()
        return render(request, 'parodynews/content_detail.html', {
            'form': form,
            'generated_content': generated_content
        })
    
    def delete(self, request):
        content_id = request.POST.get('content_id')
        content = get_object_or_404(Content, id=content_id)
        content.delete()
        messages.success(request, "Content deleted successfully!")
        return redirect('manage_content')


# View to get Assistant instructions
@login_required
def get_assistants(request):
    assistant_id = request.GET.get('assistant_id')
    instructions = ''
    assistant = ''  # Initialize assistant variable
    if assistant_id:
        try:
            assistant_obj = Assistant.objects.get(assistant_id=assistant_id)
            instructions = assistant_obj.instructions
            assistant = assistant_obj.name  # Assuming you want to return the assistant's name
            # If you have a specific field for assistant, replace assistant_obj.name with assistant_obj.<field_name>
        except Assistant.DoesNotExist:
            instructions = 'Assistant not found.'
            assistant = None  # Set assistant to None or an appropriate value if the assistant does not exist
    return JsonResponse({'instructions': instructions, 'assistant': assistant})

# View to manage assistants
@login_required
def manage_assistants(request):
    if request.method == 'POST':
        form = AssistantForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            instructions = form.cleaned_data['instructions']
            model = form.cleaned_data['model']

            # Create an assistant using your custom function
            assistant = create_assistant(name, description, instructions, model)

            # Initialize the OpenAI client
            client = OpenAI()

            # Retrieve the assistant details from OpenAI using the assistant ID
            assistant_id = assistant.id
            my_assistant = client.beta.assistants.retrieve(assistant_id)

            # Now, save the assistant details to the database
            db_assistant = Assistant(
                assistant_id=assistant_id,
                name=name,
                description=my_assistant.description,
                instructions=instructions,
                object=my_assistant.object,
                model=my_assistant.model,
                created_at=datetime.fromtimestamp(my_assistant.created_at),
                tools=my_assistant.tools,
                metadata=my_assistant.metadata,
                temperature=my_assistant.temperature,
                top_p=my_assistant.top_p,
                response_format=my_assistant.response_format,
            )
            db_assistant.save()
            messages.success(request, "Assistant created successfully.")
            
            # Redirect to the same page or a confirmation page to prevent form resubmission
            return redirect('manage_assistants')  # Replace 'manage_assistants' with the name of your view or URL pattern

    # This part is executed for GET requests and after redirecting
    form = AssistantForm()  # Always provide a fresh form for new entries
    assistants_info = Assistant.objects.all()  # Retrieve the list of assistants from the database

    # Render the template with the context
    return render(request, 'parodynews/assistant_detail.html', {
        'form': form,
        'assistants_info': assistants_info
    })

# View to delete an assistant
@login_required
def delete_assistant(request, assistant_id):
    from .utils import delete_assistant
    # Call the delete function from utils.py
    response_message = delete_assistant(assistant_id)
    # Optionally, add a success message
    messages.success(request, response_message)
    # Redirect to the list of assistants or another appropriate page
    return redirect('manage_assistants')

# View to create a new message
@login_required
@require_POST
def create_message(request):
    from .utils import create_message  # Import the utils module
    content_id = request.POST.get('content_id')
    try:
        content = Content.objects.get(id=content_id)
    except Content.DoesNotExist:
        return HttpResponseBadRequest("The requested content does not exist.")

    # Call utils.create_message to get message and thread_id
    message, thread_id = create_message(content.content)

    # Create a new Thread instance and save it
    new_thread = Thread(thread_id=thread_id)  # Assuming Thread model doesn't require any mandatory fields
    new_thread.save()

    print(f"New thread created with ID: {content_id}")

    # Create and save the new Message instance with the thread_id
    new_message = Message(message_id=message.id, content_id=content_id, thread_id=new_thread.thread_id)
    new_message.save()

    messages.success(request, "Message created successfully.")
    return redirect('list_messages')

# View to delete a message
@login_required
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

@login_required
def message_detail(request, message_id=None):
    # Check if the request method is GET
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response if not a GET request
        return HttpResponseNotAllowed(['GET'])

    message_list = Message.objects.all()  # Retrieve all messages
    assistants = Assistant.objects.all()  # Fetch all assistants
    current_message = None

    if message_id:
        current_message = get_object_or_404(Message, pk=message_id)

    return render(request, 'parodynews/message_detail.html', {'message_list': message_list, 'current_message': current_message, 'assistants': assistants})


# View to assign an assistant to a message
@login_required
def assign_assistant_to_message(request, message_id):
    if request.method == 'POST':
        message_ai = get_object_or_404(Message, pk=message_id)
        assistant_id = request.POST.get('assistant_id')
        assistant = get_object_or_404(Assistant, pk=assistant_id)
        message_ai.assistant_id = assistant  # Assuming your Message model has a ForeignKey to Assistant
        message_ai.save()

        messages.success(request, "Message Assigned successfully.")
        return redirect('message_detail', message_id=message_id)  # Redirect to the messages list page or wherever appropriate
    else:
        return HttpResponse("Method not allowed", status=405)

# View to run messages
@login_required
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

# View to list all threads and messages
@login_required
def thread_detail(request, thread_id=None):
    threads = Thread.objects.all()  # Retrieve all threads
    thread_messages = []
    current_thread = None

    if thread_id:
        current_thread = get_object_or_404(Thread, pk=thread_id)
        thread_messages = openai_list_messages(thread_id)

    return render(request, 'parodynews/thread_detail.html', {'threads': threads, 'current_thread': current_thread, 'thread_messages': thread_messages})

# View to delete a thread
@require_POST
def delete_thread(request, thread_id):
    # Fetch the thread from the database or return a 404 error if not found
    thread = get_object_or_404(Thread, pk=thread_id)
    # Delete the thread
    thread.delete()
    # Redirect to a suitable page after deletion, e.g., the threads list page
    return redirect('thread_detail')  # Replace 'threads_list' with the name of your threads list view

# View to add a message to the database
@login_required
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
        prompt= Assistant.objects.get(assistant_id=assistant_id).instructions,  # Assuming you want to use the message_content as the prompt
        assistant= Assistant.objects.get(assistant_id=assistant_id),  # Assuming you want to use the message_content as the prompt
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

@login_required
@require_POST
def update_content(request, content_id):
    try:
        # Assuming 'content' is the field name of the text you want to update
        # and 'YourContentModel' is the name of your model
        content = Content.objects.get(id=content_id)
        updated_text = request.POST.get('content', '')  # Get the updated content text from the request
        
        # Update the content text
        content.content = updated_text
        content.save()
        
        # Return a success response
        return JsonResponse({'status': 'success', 'message': 'Content updated successfully.'})
    except ObjectDoesNotExist:
        # Return an error response if the content is not found
        return JsonResponse({'status': 'error', 'message': 'Content not found.'}, status=404)
    except Exception as e:
        # Return a generic error response for any other exceptions
        return JsonResponse({'status': 'error', 'message': 'An error occurred.'}, status=500)



from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

def get_raw_content(request):
    content_id = request.GET.get('id')
    if not content_id:
        return JsonResponse({'error': 'Missing content ID'}, status=400)

    # Fetch the raw content from the database
    content = get_object_or_404(Content, pk=content_id)  # Adjust query as needed

    # Assuming the raw content is stored in a field named 'content'
    return HttpResponse(content.content, content_type='text/plain')

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Content  # Adjust with your actual model
from django.core.exceptions import ObjectDoesNotExist

@csrf_exempt  # Use this decorator to exempt this view from CSRF verification, consider CSRF protection alternatives
@require_http_methods(["POST"])  # Ensure that only POST requests are accepted
def save_edited_content(request):
    try:
        # Assuming the request body is JSON
        data = json.loads(request.body)
        content_id = data.get('contentId')
        edited_content = data.get('editedContent')

        # Update the content in the database
        content = Content.objects.get(pk=content_id)
        content.content = edited_content  
        content.save()

        return JsonResponse({'message': 'Content updated successfully'}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Content not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)