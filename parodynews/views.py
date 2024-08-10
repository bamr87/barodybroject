import json
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django import utils
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.http import require_POST
from django.views import View
from datetime import datetime
from .forms import AssistantForm, ContentForm, ContentDetailForm
from .models import Assistant, Content, ContentDetail, Message, Thread
from .utils import (
    create_assistant, 
    update_assistant,
    delete_assistant, 
    create_run, 
    generate_content, 
    openai_list_messages, 
    retrieve_assistants_info,
    create_message,
    json_to_markdown,
    generate_content_detail
)

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
            content_detail = ContentDetail.objects.get(id=content.detail_id)
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
        
        if request.POST.get('_method') == 'update':
            return self.update(request)

        form = ContentForm(request.POST)
        if form.is_valid():

            # Generate content based on the form's role and prompt
            instructions = form.cleaned_data['instructions']
            prompt = form.cleaned_data['prompt']

            generated_content_response = generate_content(instructions, prompt)
            generated_content = json.loads(generated_content_response)
            
            # Extract the title, description, and author from the generated content
            
            metadata = generated_content.get('Metadata', {})
            title = metadata.get('title', 'Default Title')
            description = metadata.get('description', 'Default Description')
            author = metadata.get('author', {})
            author_name = author.get('name', 'Default Author')
            slug = metadata.get('slug', metadata)

            # Save the content details to the database
            content_detail = ContentDetail(title=title, description=description, author=author_name, slug=slug)
            content_detail.save()
            
            content_text = json_to_markdown(generated_content.get('Content'))

            if content_text == "None":
                content_text = json_to_markdown(generated_content_response)
            
            # Save the content to the database
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
        
        # Delete the associated ContentDetail
        content_detail = get_object_or_404(ContentDetail, content=content)
        content_detail.delete()
        
        # Delete the Content
        content.delete()
        
        messages.success(request, "Content and its details deleted successfully!")
        return redirect('manage_content')



@csrf_exempt  # Use this decorator to exempt this view from CSRF verification, consider CSRF protection alternatives
@require_http_methods(["GET", "POST"])  # Ensure that only GET and POST requests are accepted
def update_content(request, content_id):
    content_detail = get_object_or_404(ContentDetail, id=content_id)
    content = get_object_or_404(Content, id=content_detail.content.id)  # Assuming ContentDetail has a ForeignKey to Content

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check if the request is an AJAX request
            try:
                data = json.loads(request.body)
                form_type = data.get('formType')  # Get the form type from the request data

                if form_type == 'content-detail':
                    content_detail_form = ContentDetailForm(data, instance=content_detail)
                    if content_detail_form.is_valid():
                        content_detail_form.save()
                        return JsonResponse({'message': 'ContentDetail updated successfully'}, status=200)
                    else:
                        return JsonResponse({'error': content_detail_form.errors}, status=400)
                elif form_type == 'content':
                    content_form = ContentForm(data, instance=content)
                    if content_form.is_valid():
                        content_form.save()
                        return JsonResponse({'message': 'Content updated successfully'}, status=200)
                    else:
                        return JsonResponse({'error': content_form.errors}, status=400)
                else:
                    return JsonResponse({'error': 'Invalid form type'}, status=400)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Content not found'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            content_detail_form = ContentDetailForm(request.POST, instance=content_detail)
            content_form = ContentForm(request.POST, instance=content)

            if content_detail_form.is_valid() and content_form.is_valid():
                content_detail_form.save()
                content_form.save()
                messages.success(request, "Content updated successfully!")
                return redirect(reverse('content_detail', args=[content_id]))
    else:
        content_detail_form = ContentDetailForm(instance=content_detail)
        content_form = ContentForm(instance=content)

    return render(request, 'parodynews/content_detail.html', {
        'content_detail_form': content_detail_form,
        'content_form': content_form,
        'selected_content': content_detail
    })

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
def manage_assistants(request, assistant_id=None):
    if assistant_id:
        assistant = get_object_or_404(Assistant, pk=assistant_id)
        is_edit = True
    else:
        assistant = None
        is_edit = False
    if request.method == 'POST':
        form = AssistantForm(request.POST, instance=assistant)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            instructions = form.cleaned_data['instructions']
            model = form.cleaned_data['model']

            if is_edit:
                # Update the existing assistant
                assistant.name = name
                assistant.description = description
                assistant.instructions = instructions
                assistant.model = model
                assistant.save()

                # Update the assistant on OpenAI
                update_assistant(assistant.assistant_id, name, instructions, model)

                messages.success(request, "Assistant updated successfully.")
                return redirect('manage_assistants')  # Replace 'manage_assistants' with the name of your view or URL pattern

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
            return redirect('manage_assistants')  # Replace 'manage_assistants' with the name of your view or URL pattern
        else:
            # If the form is not valid, render the form with errors
            return render(request, 'parodynews/assistant_detail.html', {
                'form': form,
                'assistants_info': Assistant.objects.all(),
                'is_edit': is_edit
            })
    else:
        form = AssistantForm(instance=assistant)
    return render(request, 'parodynews/assistant_detail.html', {
        'form': form,
        'assistants_info': Assistant.objects.all(),
        'is_edit': is_edit
    })
            # Redirect to the same page or a confirmation page to prevent form resubmission

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