import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.views import View
from datetime import datetime
from .forms import AssistantForm, ContentItemForm, ContentDetailForm
from .models import Assistant, ContentItem, ContentDetail, Message, Thread
from .utils import (
    save_assistant, 
    openai_delete_assistant, 
    create_run, 
    generate_content, 
    openai_create_message,
    openai_delete_message,
    openai_list_messages, 
    retrieve_assistants_info,
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
            content = ContentItem.objects.get(detail_id=content_detail_id, line_number=1)
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
        content_form = ContentItemForm(instance=content)
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
            'display_fields': display_fields,
            'instructions': instructions,
        })

    def post(self, request, content_detail_id=None):
        if request.POST.get('_method') == 'delete':
            return self.delete(request)
        
        if request.POST.get('_method') == 'save':
            return self.save(request)

        if request.POST.get('_method') == 'generate_content':
            return self.generate_content(request)
        
        if request.POST.get('_method') == 'create_thread':
            return self.create_thread(request)

        return redirect('manage_content')
    
    def save(self, request, content_detail=None):
        content_detail_id = request.POST.get('content_detail_id')

        content_form = ContentItemForm(request.POST)
        content_detail_form = ContentDetailForm(request.POST)

        # Check if content_detail_id is provided
        if content_detail_id:
            content_detail = ContentDetail.objects.get(pk=content_detail_id)
            content = ContentItem.objects.get(detail_id=content_detail, line_number=1)

            content_form = ContentItemForm(request.POST, instance=content)
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

    def generate_content(self, request, content_detail=None):
        content_detail_id = request.POST.get('content_detail_id')
        content_form = ContentItem.objects.get(detail_id=content_detail_id)
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        data, content_detail_schema = generate_content(content_form)
        json_data = json.loads(content_detail_schema)
           # Check if data is in JSON format
        try:
            content_data = json.loads(data)
        except json.JSONDecodeError:
            content_data = data

        content_section = content_data['Content']['body'] if isinstance(content_data, dict) else content_data

        content_form.content = content_section
        content_form.save()

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

    def create_thread(self, request):
        content_detail_id = request.POST.get('content_detail_id')

        content = ContentItem.objects.get(detail_id=content_detail_id, line_number=1)
        content_id = content.id

        # Call utils.create_message to get message and thread_id
        message, thread_id = openai_create_message(content)

        # Create a new Thread instance and save it
        new_thread = Thread(id=thread_id, name=content.detail.title)
        new_thread.save()

        print(f"New thread created with ID: {content_id}")

        # Create and save the new Message instance with the thread_id
        new_message = Message(id=message.id, content_id=content_id, thread_id=new_thread.id)
        new_message.save()

        messages.success(request, "Message created successfully.")
        return redirect('thread_message_detail', message_id=new_message.id, thread_id=new_thread.id)


    def delete(self, request, content_detail_id=None):
        content_detail_id = request.POST.get('content_detail_id')
        content_detail = ContentDetail.objects.get(pk=content_detail_id)
        content = ContentItem.objects.filter(detail_id=content_detail_id)
        content_detail.delete()
        content.delete()
        messages.success(request, "Content and its details deleted successfully!")
        return redirect('manage_content')

class ProcessContentView(LoginRequiredMixin, ModelFieldsMixin, View):
    template_name = 'parodynews/content_processing.html'
    model = Thread
    # View to list all threads and messages

    def get(self, request, message_id=None, thread_id=None):
        threads = Thread.objects.all()  # Retrieve all threads
        thread_messages = []
        current_thread = None
        current_message = None
        fields, display_fields = self.get_model_fields()

        if thread_id:
            current_thread = Thread.objects.get(pk=thread_id)
            thread_messages = Message.objects.filter(thread_id=thread_id)

        if message_id:
            current_message = Message.objects.get(pk=message_id)

        message_list = Message.objects.all()
        assistants = Assistant.objects.all()  # Fetch all assistants

        return render(request, 'parodynews/content_processing.html', {
            'threads': threads,
            'message_list': message_list,
            'current_thread': current_thread,
            'assistants': assistants,
            'thread_messages': thread_messages,
            'current_message': current_message,
            'fields': fields,
            'display_fields': display_fields
            })

    def post(self, request, thread_id=None, message_id=None):
        if request.POST.get('_method') == 'delete':
            return self.delete_thread(request, thread_id)

        if request.POST.get('_method') == 'delete_thread_message':
            return self.delete_thread_message(request, message_id, thread_id)
        
        if request.POST.get('_method') == 'run_message':
            return self.run_message(request)
        

    # View to delete a thread

    def delete_thread(self, request, thread_id=None):
        # Fetch the thread from the database
        thread = Thread.objects.get(pk=thread_id)
        # Delete the thread
        thread.delete()
        client = OpenAI()

        client.beta.threads.delete(thread_id)
        messages.success(request, "Thread deleted successfully.")

        # Redirect to a suitable page after deletion, e.g., the threads list page
        return redirect('process_content')  # Replace 'threads_list' with the name of your threads list view

    def delete_thread_message(self, request, message_id, thread_id):
        # Retrieve the message instance
        message = Message.objects.get(id=message_id)

        # Delete the message
        message.delete()

        # Delete the message from OpenAI
        openai_delete_message(message_id, thread_id)

        messages.success(request, "Message deleted successfully.")
        return redirect('thread_detail', thread_id=thread_id)

    # View to run messages
    def run_message(self, request, message_id=None, thread_id=None):
        # retrieve the message instance of the selected message
        message_id = request.POST.get('message_id')
        message = Message.objects.get(id=message_id)  # Retrieve the message by its ID or return 404
        assistant_id = request.POST.get('assistant_id')  # Assuming assistant_id is passed in the request
        thread_id = message.thread_id  # Access the thread_id associated with the message
        
        # Call the create_run function to create a run for the message
        run, run_status, message_data = create_run(thread_id, assistant_id)  
        
        # Update the message status and run_id
        message.status = run_status.status
        message.run_id = run.id
        message.save()

        # Create a new content item instance with the response content
        new_content = ContentItem.objects.create(
            assistant_id=assistant_id,
            prompt=Assistant.objects.get(id=assistant_id).instructions,
            content=message_data['text'],
            detail_id=message.content.detail_id,
            content_type='message'
        )

        # Create a new message instance with the response content
        new_message = Message.objects.create(
            id=message_data['id'],
            thread_id=thread_id,
            assistant_id=None,
            status=run_status.status,
            run_id=run.id,
            content_id=new_content.id,
        )
        
        new_content.save()
        new_message.save()

        messages.success(request, "Message run successfully.")

        # Redirect to the thread_detail.html of the message
        return redirect('thread_message_detail', message_id=message_id, thread_id=thread_id)





class ManageMessageView(LoginRequiredMixin, View):
    template_name = 'parodynews/message_detail.html'

    def get(self, request, message_id=None):

        message_list = Message.objects.all()
        assistants = Assistant.objects.all()  # Fetch all assistants
        current_message = None

        if message_id:
            current_message = Message.objects.get(pk=message_id)

        return render(request, 'parodynews/message_detail.html', {
            'message_list': message_list,
            'current_message': current_message,
            'assistants': assistants
            }
        )

    def post(self, request, message_id=None, thread_id=None, assigned_assistant_id=None):
        if request.POST.get('_method') == 'create_message':
            return self.create_message(request)
        
        if request.POST.get('_method') == 'delete_message':
            return self.delete_message(request, message_id, thread_id)
        
        if request.POST.get('_method') == 'assign_assistant_to_message':
            return self.assign_assistant_to_message(request, message_id)

    def delete_message(self, request, message_id, thread_id):
        # Retrieve the message instance
        message = Message.objects.get(id=message_id)

        # Delete the message
        message.delete()

        # Delete the message from OpenAI
        openai_delete_message(message_id, thread_id)

        messages.success(request, "Message deleted successfully.")
        return redirect('manage_message')  # Redirect to the messages list page or wherever appropriate
    # View to assign an assistant to a message

    def assign_assistant_to_message(self, request, message_id, thread_id=None):
        assigned_assistant_id= request.POST.get('assigned_assistant_id')
        thread_id= request.POST.get('thread_id')
        
        message = Message.objects.get(pk=message_id)
        assistant = Assistant.objects.get(pk=assigned_assistant_id)
        message.assistant_id = assistant  # Assuming your Message model has a ForeignKey to Assistant
        
        message.save()
        
        messages.success(request, "Message Assigned successfully.")

        if thread_id:
            return redirect('thread_message_detail', thread_id=thread_id, message_id=message_id)
        return redirect('message_detail', message_id=message_id)  # Redirect to the messages list page or wherever appropriate


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
        Assistant.objects.get(id=assistant_id).delete()
        response_message = openai_delete_assistant(assistant_id)
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
    title = generated_content_detail['Header']['title'],  # Placeholder title, adjust as needed
    description = generated_content_detail['Metadata']['description'],  # Placeholder description, adjust as needed
    author = generated_content_detail['Header']['author']['name'],  # Access the nested 'name' key within 'author'
    published_at = datetime.now().isoformat(),  # Use the current time for published_at
    slug = generated_content_detail['Metadata']['slug']  # Access the 'slug' key)
    
    content_detail = ContentDetail.objects.create(
        title=title[0],
        description=description[0],
        author=author[0],
        published_at=published_at[0],
        slug=slug[0]
        )
    # Retrieve the ContentDetail instance using the ID
    content_detail_instance = ContentDetail.objects.get(id=content_detail.id)

    # Then, create or update the Content object with the content_detail instance
    content, _ = ContentItem.objects.update_or_create(
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
    content = get_object_or_404(ContentItem, pk=content_id)  # Adjust query as needed

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
from .models import ContentDetail, ContentItem
from .utils import generate_markdown_file
import yaml

def generate_markdown_view(request):
    content_id = request.GET.get('content_id')
    content_detail = get_object_or_404(ContentDetail, id=content_id)
    
    # Fetch the related Content object
    content = get_object_or_404(ContentItem, detail_id=content_detail.id)
    
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
