import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.http import require_POST
from django.views import View
from datetime import datetime
from .forms import AssistantForm, ContentForm, ContentDetailForm
from .models import Assistant, Content, ContentDetail, Message, Thread
from .utils import (
    save_assistant, 
    delete_assistant, 
    create_run, 
    generate_content, 
    openai_list_messages, 
    retrieve_assistants_info,
    create_message,
    json_to_markdown,
    generate_content_detail
)

from .mixins import ModelFieldsMixin


print("Loading views.py")

from openai import OpenAI

# Custom LoginView to render a custom login page
class UserLoginView(LoginView):
    template_name = 'login.html'

# View to render the index page
def index(request):
    # This view will render the root index page
    return render(request, 'parodynews/index.html', {})

# View to manage content creation and deletion

class ManageContentView(LoginRequiredMixin, ModelFieldsMixin, View):
    model=ContentDetail
    template_name = 'parodynews/content_detail.html'

    def get(self, request, content_detail_id=None, content_id=None):
        # Check if content_id is provided
        if content_detail_id:
            content_detail = ContentDetail.objects.get(pk=content_detail_id)
            content = Content.objects.get(detail_id=content_detail_id)
            content_id = content.id
            assistant = content.assistant.name if content.assistant else None
            instructions = content.assistant.instructions if content.assistant else None
            is_edit = True
        else:
            content = None
            content_detail = None
            assistant = None
            instructions = None
            is_edit = False

        # Initialize the forms
        content_form = ContentForm(instance=content, initial={'assistant': assistant, 'instructions': instructions})
        content_detail_form = ContentDetailForm(instance=content_detail)

        # Get the fields and display fields for the model
        content_detail_info = ContentDetail.objects.all()
        fields, display_fields = self.get_model_fields()

        # Render the content detail page with the forms and content details
        return render(request, self.template_name, {
            'content_form': content_form,
            'content_detail_form': content_detail_form,
            'content_detail_info': content_detail_info,
            'content_detail_id': content_detail_id,
            'content_id': content_id,
            'assistant': assistant,
            'fields': fields,
            'display_fields': display_fields
        })

    def post(self, request, content_detail_id=None):
        if request.POST.get('_method') == 'delete':
            return self.delete(request)
        
        if request.POST.get('_method') == 'save':
            return self.save(request)

        if request.POST.get('_method') == 'run':
            return self.run(request)
        
        return redirect('content_detail', content_detail_id=content_detail_id)
    
    def save(self, request, content_detail=None):
        content_detail_id = request.POST.get('content_detail_id')

        content_form = ContentForm(request.POST)
        content_detail_form = ContentDetailForm(request.POST)

        # Check if content_detail_id is provided
        if content_detail_id:
            content_detail = ContentDetail.objects.get(pk=content_detail_id)
            content = Content.objects.get(detail_id=content_detail)

            content_form = ContentForm(request.POST, instance=content)
            content_detail_form = ContentDetailForm(request.POST, instance=content_detail)

        # Save the forms if they are valid
        if content_form.is_valid() and content_detail_form.is_valid():
            content_detail = content_detail_form.save(commit=False)
            content_detail.save()
            content = content_form.save(commit=False)
            content.detail = content_detail
            content.save()
            
            messages.success(request, "Content and its details saved successfully!")
            return redirect('content_detail', content_detail_id=content_detail.id)
        else:
            error_messages = f"Content form errors: {content_form.errors}, Content detail form errors: {content_detail_form.errors}"
            messages.error(request, f"Error saving content and its details! {error_messages}")

        return self.get(request)

    def run(self, request, content_detail=None):
        content_form = ContentForm(request.POST)
        data = generate_content(content_form)
        content_detail_id = request.POST.get('content_detail_id')
        content = Content.objects.get(detail_id=content_detail_id)
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        json_data = json.loads(data)
        content_section = json_data['Content']['body']
        content.content = content_section
        content.save()

        content_detail_section = json_data['Header']
        content_detail.title = content_detail_section['title']
        content_detail.author = content_detail_section['author']['name']
        content_detail.published_at = datetime.now()

        content_detail_metadata = json_data['Metadata']
        content_detail.description = content_detail_metadata['description']
        content_detail.slug = content_detail_metadata['slug']

        content_detail.save()

        messages.success(request, "Content generated successfully")

        return redirect('content_detail', content_detail_id=content_detail_id)

    def delete(self, request, content_detail_id=None):
        content_detail_id = request.POST.get('content_detail_id')
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        content = Content.objects.filter(detail_id=content_detail_id)
        content_detail.delete()
        content.delete()
        messages.success(request, "Content and its details deleted successfully!")
        return redirect('manage_content')

class ManageMessageView(LoginRequiredMixin, View):
    template_name = 'parodynews/message_detail.html'

    def post(self, request, *args, **kwargs):
        if request.POST.get('_method') == 'create_message':
            return self.create_message(request)

    def get(self, request, message_id=None):

        message_list = Message.objects.select_related('content__detail').all()
        assistants = Assistant.objects.all()  # Fetch all assistants
        current_message = None

        if message_id:
            current_message = get_object_or_404(Message, pk=message_id)

        return render(request, 'parodynews/message_detail.html', {
            'message_list': message_list,
            'current_message': current_message,
            'assistants': assistants
            }
        )

        
    def create_message(self, request):
        content_detail_id = request.POST.get('content_detail_id')

        content = Content.objects.get(detail_id=content_detail_id)
        content_id = content.id

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
        return redirect(reverse_lazy('message_detail', kwargs={'message_id': new_message.message_id}))




from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import Assistant, JSONSchema
from .forms import AssistantForm

class ManageAssistantsView(ModelFieldsMixin, View):
    model = Assistant
    template_name = 'parodynews/assistant_detail.html'
    
    def get(self, request, assistant_id=None):
        # Check if assistant_id is provided
        if assistant_id:
            assistant = Assistant.objects.get(pk=assistant_id)
            is_edit = True
        else:
            assistant = None
            is_edit = False

        # Initialize the form
        assistant_form = AssistantForm(instance=assistant)

        # Get the fields and display fields for the model
        assistants_info = Assistant.objects.all()
        fields, display_fields = self.get_model_fields()

        # Render the assistant detail page with the form and assistant details
        return render(request, self.template_name, {
            'assistant_form': assistant_form,
            'assistants_info': assistants_info,
            'assistant_id': assistant_id,
            'is_edit': is_edit,
            'fields' : fields,
            'display_fields': display_fields
        })

    def post(self, request, assistant_id=None):
        if request.POST.get('_method') == 'delete':
            return self.delete(request)

        if request.POST.get('_method') == 'save':
            return self.save(request)

        return redirect('assistant_detail', assistant_id=assistant_id)

    def save(self, request, assistant=None):
        assistant_id = request.POST.get('assistant_id')

        assistant_form = AssistantForm(request.POST)

        if assistant_id:
            assistant = Assistant.objects.get(pk=assistant_id)
            assistant_form = AssistantForm(request.POST, instance=assistant)

        if assistant_form.is_valid():
            assistant = assistant_form.save(commit=False)

            # Create or update the assistant in OpenAI
            assistant_ai = save_assistant(assistant.name, assistant.description, assistant.instructions, assistant.model, assistant.json_schema, assistant.id)
            assistant.id = assistant_ai.id
            assistant.save()

            messages.success(request, "Assistant created successfully.")
            return redirect('manage_assistants')
        else:
            messages.error(request, "Error creating assistant.")
            assistants_info = Assistant.objects.all()
            fields = Assistant._meta.get_fields()
            display_fields = Assistant().get_display_fields()
            return render(request, self.template_name, {
                'assistant_form': assistant_form,
                'assistants_info': assistants_info,
                'fields': fields,
                'display_fields': display_fields,

            })

    def delete(self, request, assistant_id=None):
        assistant_id = request.POST.get('assistant_id')
        response_message = delete_assistant(assistant_id)
        messages.success(request, response_message)
        return redirect('manage_assistants')

def get_assistant_details(request, assistant_id):
    try:
        assistant = Assistant.objects.get(id=assistant_id)
        instructions = assistant.instructions  # Assuming 'instructions' is a field in the Assistant model

        data = {
            'assistant_id': assistant.id,
            'instructions': instructions,
        }
        return JsonResponse(data)
    except Assistant.DoesNotExist:
        return JsonResponse({'error': 'Assistant not found'}, status=404)



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
    return redirect('manage_message')  # Redirect to the messages list page or wherever appropriate



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

    generated_content_detail = json.loads(generate_content_detail(message_content))
    # First, create the ContentDetail object
    content_detail = ContentDetail.objects.create(
        title=generated_content_detail.get('title'),  # Placeholder title, adjust as needed
        description=generated_content_detail['description'],  # Placeholder description, adjust as needed
        author=generated_content_detail['author']['name'],  # Access the nested 'name' key within 'author'
        published_at=datetime.now(),  # Use the current time for published_at
        slug = generated_content_detail.get('slug'))
    # Retrieve the ContentDetail instance using the ID
    content_detail_instance = ContentDetail.objects.get(id=content_detail.id)

    # Then, create or update the Content object with the content_detail instance
    content, _ = Content.objects.update_or_create(
        prompt= Assistant.objects.get(id=assistant_id).instructions,  # Assuming you want to use the message_content as the prompt
        assistant= Assistant.objects.get(id=assistant_id),  # Assuming you want to use the message_content as the prompt
        content=message_content,
        detail=content_detail_instance  # Use the ContentDetail instance here
    )

    # Update content_detail to link to the newly created or updated content
    content_detail.content.set([content])
    content_detail.save()

    # Create or update the Message object
    message = Message.objects.update_or_create(
        message_id=message_id,
        thread_id=thread_id,
        defaults={'content': content, 'created_at': datetime.now()}
    )
    messages.success(request, "Message and content created successfully.")

    return redirect('thread_detail')  # Redirect back to the thread detail page


def get_raw_content(request):
    content_id = request.GET.get('id')
    if not content_id:
        return JsonResponse({'error': 'Missing content ID'}, status=400)

    # Fetch the raw content from the database
    content = get_object_or_404(Content, pk=content_id)  # Adjust query as needed

    # Assuming the raw content is stored in a field named 'content'
    return HttpResponse(content.content, content_type='text/plain')

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from .models import MyObject
from .forms import MyObjectForm

class MyObjectView(View):
    template_name = 'object_template.html'
    success_url = reverse_lazy('object-list')

    def get(self, request, pk=None, action=None):
        if action == 'delete' and pk:
            obj = get_object_or_404(MyObject, pk=pk)
            return render(request, self.template_name, {
                'object': obj,
                'object_list': MyObject.objects.all(),
                'action': 'delete'
            })

        if pk:
            obj = get_object_or_404(MyObject, pk=pk)
            form = MyObjectForm(instance=obj)
            action = 'update'
        else:
            form = MyObjectForm()
            obj = None
            action = 'create'

        objects = MyObject.objects.all()
        return render(request, self.template_name, {
            'form': form,
            'object': obj,
            'object_list': objects,
            'action': action,
        })

    def post(self, request, pk=None, action=None):
        if action == 'delete' and pk:
            obj = get_object_or_404(MyObject, pk=pk)
            obj.delete()
            return redirect(self.success_url)

        if pk:
            obj = get_object_or_404(MyObject, pk=pk)
            form = MyObjectForm(request.POST, instance=obj)
            action = 'update'
        else:
            form = MyObjectForm(request.POST)
            obj = None
            action = 'create'

        if form.is_valid():
            form.save()
            return redirect(self.success_url)

        objects = MyObject.objects.all()
        return render(request, self.template_name, {
            'form': form,
            'object': obj,
            'object_list': objects,
            'action': action,
        })
    

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import ContentDetail, Content
from .utils import generate_markdown_file
import yaml

def generate_markdown_view(request):
    content_id = request.GET.get('content_id')
    content_detail = get_object_or_404(ContentDetail, id=content_id)
    
    # Fetch the related Content object
    content = get_object_or_404(Content, detail_id=content_detail.id)
    
    # Create the frontmatter as a dictionary
    frontmatter = {
        'title': content_detail.title,
        'description': content_detail.description,
        'author': content_detail.author,
        'published_at': content_detail.published_at.strftime("%Y-%m-%d"),
        'slug': content_detail.slug,
    }
    
    # Convert the frontmatter dictionary to a YAML string
    frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
    
    # Combine the frontmatter and the main content
    data = f"---\n{frontmatter_yaml}---\n\n{content.content}"
    
    # Format the date and title for the filename
    filename = content_detail.slug.lower().replace(" ", "-")
    date_str = content_detail.published_at.strftime("%Y-%m-%d")
    formatted_filename = f"{date_str}-{filename}.md"

    # Generate the markdown file
    file_path = generate_markdown_file(data, formatted_filename)
    
    # Provide feedback to the user
    return HttpResponse(f"Markdown file generated at: {file_path}")


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import JSONSchema
from .forms import JSONSchemaForm

def list_schemas(request):
    schemas = JSONSchema.objects.all()
    return render(request, 'parodynews/schema_detail.html', {'schemas': schemas})

def create_schema(request):
    if request.method == 'POST':
        form = JSONSchemaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schema created successfully.')
            return redirect('list_schemas')
    else:
        form = JSONSchemaForm()
    return render(request, 'parodynews/schema_form.html', {'form': form})

def edit_schema(request, pk):
    schema = get_object_or_404(JSONSchema, pk=pk)
    if request.method == 'POST':
        form = JSONSchemaForm(request.POST, instance=schema)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schema updated successfully.')
            return redirect('list_schemas')
    else:
        form = JSONSchemaForm(instance=schema)
    return render(request, 'parodynews/schema_form.html', {'form': form})

def export_schema(request, pk):
    schema = get_object_or_404(JSONSchema, pk=pk)
    response = JsonResponse(schema.schema)
    response['Content-Disposition'] = f'attachment; filename="{schema.name}.json"'
    return response

def delete_schema(request, pk):
    schema = get_object_or_404(JSONSchema, pk=pk)
    if request.method == 'POST':
        schema.delete()
        messages.success(request, 'Schema deleted successfully.')
        return redirect('list_schemas')
    return redirect('list_schemas')
