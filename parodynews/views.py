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
from .models import (
    Assistant,
    ContentItem,
    ContentDetail,
    Message,
    Thread,
    PoweredBy,
    Post,
    PostFrontMatter,
)
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

from django.views.generic import TemplateView

class FooterView(TemplateView):
    template_name = 'footer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['powered_by'] = PoweredBy.objects.all()
        return context

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
            content_form = ContentItemForm(instance=content)
            content_detail_form = ContentDetailForm(instance=content_detail)
        else:
            content = None
            content_detail = None
            assistant = None
            instructions = None
            content_form = ContentItemForm()
            content_detail_form = ContentDetailForm()

        # Initialize the forms

        # Get the fields and display fields for the model
        content_detail_info = ContentDetail.objects.all()
        fields, display_fields = self.get_model_fields()

        context = {
            'content_form': content_form,
            'content_detail_form': content_detail_form,
            'content_id': content_id,
            'content_detail_id': content_detail_id,
            'assistant': assistant,
            'instructions': instructions,
            'content_detail_info': content_detail_info,
            'fields': fields,
            'display_fields': display_fields,
        }

        # Render the content detail page with the forms and content details
        return render(request, self.template_name, context)

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

        # initialize the forms 
        content_form = ContentItemForm(request.POST)
        content_detail_form = ContentDetailForm(request.POST)

        # Get the fields and display fields for the model
        content_detail_info = ContentDetail.objects.all()
        fields, display_fields = self.get_model_fields()

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
            
            # Pass the forms back to the context to preserve the data
            context = {
                'content_form': content_form,
                'content_detail_form': content_detail_form,
                'content_detail_info': content_detail_info,
                'fields': fields,
                'display_fields': display_fields,
            }            

            return render(self.request, self.template_name, context)

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
        # Check if thread_id is provided
        thread_messages = []
        current_thread = None
        current_message = None
      
        if thread_id:
            current_thread = Thread.objects.get(pk=thread_id)
            thread_messages = Message.objects.filter(thread_id=thread_id)

        threads = Thread.objects.all()  # Retrieve all threads
        fields, display_fields = self.get_model_fields()

        if message_id:
            current_message = Message.objects.get(pk=message_id)

        message_list = Message.objects.all()
        assistants = Assistant.objects.all()  # Fetch all assistants

        return render(request, 'parodynews/content_processing.html', {
            'message_list': message_list,
            'current_thread': current_thread,
            'threads': threads,
            'assistants': assistants,
            'thread_messages': thread_messages,
            'current_message': current_message,
            # 'thread_run_form': ThreadRunFrom(),
            'fields': fields,
            'display_fields': display_fields
            })

    def post(self, request, thread_id=None, message_id=None):
        if request.POST.get('_method') == 'delete':
            return self.delete_thread(request, thread_id)

        if request.POST.get('_method') == 'delete_thread_message':
            return self.delete_thread_message(request, message_id, thread_id)
        
        if request.POST.get('_method') == 'create_content':
            return self.create_content(request)
        
        if request.POST.get('_method') == 'run_message':
            return self.run_message(request)
        
        if request.POST.get('_method') == 'create_post':
            return self.create_post(request)

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

    def create_content(self, request, thread_id=None, message_id=None):
        message_id = request.POST.get('message_id')
        message = Message.objects.get(id=message_id)
        message_content = message.content.content
        thread_id = request.POST.get('thread_id')
        assistant_id = message.assistant_id

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
            prompt= message_content,  # Assuming you want to use the message_content as the prompt
            assistant= Assistant.objects.get(id=assistant_id) if assistant_id else None,  # Assuming you want to use the message_content as the prompt
            detail=content_detail_instance  # Use the ContentDetail instance here
        )

        # Update content_detail to link to the newly created or updated content
        content_detail.content.set([content])
        content_detail.save()

        messages.success(request, "Message and content created successfully.")

        return redirect('content_detail', content_detail_id=content_detail.id )  # Redirect back to the thread detail page



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
            content=message_data['content'],
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

    # View to create a post

    def create_post(self, request, content_id=None, thread_id=None, message_id=None):
        thread_id = request.POST.get('thread_id')
        message_id = request.POST.get('message_id')
        assistant_id = request.POST.get('assistant_id')
        content_id = Message.objects.get(id=message_id).content.id

        # Retrieve the message instance
        message = Message.objects.get(id=message_id)

        # Retrieve the content instance
        content = ContentItem.objects.get(id=content_id)

        content_detail = ContentDetail.objects.get(id=content.detail_id)

        assistant = Assistant.objects.get(id=assistant_id) if Assistant.objects.filter(id=assistant_id).exists() else None
        # Create a new post instance
        post = Post.objects.create(
            content=content.content,
            thread=Thread.objects.get(id=thread_id),
            message=Message.objects.get(id=message_id),
            assistant=assistant,
            content_detail=content_detail
        )

        post_frontmatter = PostFrontMatter.objects.create(
            post_id=post.id,
            title=message.content.detail.title,
            description=message.content.detail.description,
            author=message.content.detail.author,
            published_at=message.content.detail.published_at,
            slug=message.content.detail.slug,
        )

        post.save()
        post_frontmatter.save()

        messages.success(request, "Post created successfully.")
        return redirect('post_detail', post_id=post.id)




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

# parodynews/views.py
import os
from django.conf import settings
from django.shortcuts import render, redirect

from .forms import PostForm, PostFrontMatterForm
from .models import Post
from .utils import generate_markdown_file
import yaml
class ManagePostView(LoginRequiredMixin, ModelFieldsMixin, View):
    model = Post
    template_name = 'parodynews/pages_post_detail.html'

    def get(self, request, post_id=None):
        if post_id:
            post = Post.objects.get(pk=post_id)
            post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)
            form_post = PostForm(instance=post)
            form_post_frontmatter = PostFrontMatterForm(instance=post_frontmatter)

        else:
            post = None
            post_frontmatter = None
            form_post = None
            form_post_frontmatter = None

        # Initialize the form
        form_post = PostForm(instance=post)
        form_post_frontmatter = PostFrontMatterForm(instance=post_frontmatter)
        
        # Get all posts and fields
        post_list = Post.objects.all()
        fields, display_fields = self.get_model_fields()

        context = {
            'post': post,
            'form_post': form_post,
            'form_post_frontmatter': form_post_frontmatter,
            'post_list': post_list,
            'fields': fields,
            'display_fields': display_fields,
            }

        return render(request, self.template_name, context)



    def post(self, request, post_id=None):
        if request.POST.get('_method') == 'delete':
            return self.delete(request)
        
        if request.POST.get('_method') == 'save':
            return self.save(request)
        
        if request.POST.get('_method') == 'publish':
            return self.publish(request)
        
        return redirect('manage_post')
    


    def delete(self, request, post_id=None):
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        post.delete()

        messages.success(request, "Post deleted successfully.")

        return redirect('manage_post')



    def save(self, request, post_id=None):
        post_id = request.POST.get('post_id')

        # Initialize the forms
        form_post = PostForm(request.POST)
        form_post_frontmatter = PostFrontMatterForm(request.POST)

        # Get the fields and display fields for the model
        post_list = Post.objects.all()
        fields, display_fields = self.get_model_fields()

        # Check if post_id is provided
        if post_id:
            post = Post.objects.get(pk=post_id)
            post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

            form_post = PostForm(request.POST, instance=post)
            form_post_frontmatter = PostFrontMatterForm(request.POST, instance=post_frontmatter)

        # Save the forms if they are valid
        if form_post.is_valid() and form_post_frontmatter.is_valid():

            post_front_matter = form_post_frontmatter.save(commit=False)
            post_front_matter.save()

            post = form_post.save(commit=False)
            post.frontmatter = post_front_matter
            post.save()

            messages.success(request, "Post and front matter saved successfully.")
            return redirect('post_detail', post_id=post.id)
        else:
            
            if not form_post.is_valid():
                messages.error(request, form_post.errors)
            if not form_post_frontmatter.is_valid():
                messages.error(request, form_post_frontmatter.errors)
            
            context = {
                'post': post,
                'form_post': form_post,
                'form_post_frontmatter': form_post_frontmatter,
                'post_list': post_list,
                'fields': fields,
                'display_fields': display_fields,
            }

            return render(request, self.template_name, context)

    def publish(self, request, post_id=None):
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        
        # Fetch the related Post Frontmatter
        post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)
        
        # Create the frontmatter as a dictionary
        frontmatter = {
            'title': post_frontmatter.title,
            'description': post_frontmatter.description,
            'author': post_frontmatter.author,
            'published_at': post_frontmatter.published_at.strftime("%Y-%m-%d"),
            'slug': post_frontmatter.slug,
        }
        
        # Convert the frontmatter dictionary to a YAML string
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
        
        # Combine the frontmatter and the main content
        data = f"---\n{frontmatter_yaml}---\n\n{post.content}"
        
        # Format the date and title for the filename
        filename = post_frontmatter.slug.lower().replace(" ", "-")
        date_str = post_frontmatter.published_at.strftime("%Y-%m-%d")
        formatted_filename = f"{date_str}-{filename}.md"

        # Generate the markdown file
        file_path = generate_markdown_file(data, formatted_filename)
        
        # Provide feedback to the user
        return HttpResponse(f"Markdown file generated at: {file_path}")
        
