from django.shortcuts import render, redirect
from .forms import PostForm
from .forms import AssistantForm
from .scripts.create_jekyll_post import create_jekyll_post
from .utils import create_assistant
from openai import OpenAI  # Import OpenAI library
from .utils import retrieve_assistants_info  # Ensure this import is correct based on your project structure
from .utils import generate_content  
from .models import Post  # Import the Post model


def index(request):
    # This view will render the root index page
    return render(request, 'parodynews/index.html', {})

# Ensure the rest of your views.py file remains unchanged

# This is the view that will handle the form submission

def content_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            # Extract role and prompt from the form submission
            role = form.cleaned_data['role']
            prompt = form.cleaned_data['prompt']

            # Assume generate_content is a function that generates content based on role and prompt
            generated_content = generate_content(role, prompt)

            # Initialize the post but don't commit to the database yet
            post = form.save(commit=False)
            # Set the generated content to the post's content field
            post.content = generated_content
            # Now save the post to the database, including the generated content
            post.save()

            # Optionally, store generated_content in session for immediate use
            request.session['generated_content'] = generated_content

            # Redirect to a success page or the page where the post can be viewed
            return redirect('post_success')
    else:
        form = PostForm()
        generated_content = ""

    # Render the form page again if not POST or if form is invalid, with any generated content
    return render(request, 'parodynews/content_form.html', {'form': form, 'generated_content': generated_content})

def post_success(request):
    # Retrieve generated_content from session
    generated_content = request.session.get('generated_content', '')

    # Optionally, you can delete the session variable after retrieving it
    # del request.session['generated_content']

    return render(request, 'parodynews/post_success.html', {'generated_content': generated_content})

# New view to list the content generated

def list_content(request):
    # Retrieve all content from the database
    generated_content = Post.objects.all()

    return render(request, 'parodynews/generated_content.html', {'generated_content': generated_content})

# New view function to create an assistant

def create_assistant(request):
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
            # Assuming `assistant_id` is available from your `create_assistant` function
            assistant_id = assistant.id  # Adjusted from assistant.get('id') to assistant.id
            my_assistant = client.beta.assistants.retrieve(assistant_id)
            
            # Now you have `my_assistant` details from OpenAI, which you can use
            # For demonstration, let's pass both local and OpenAI assistant details to a template:

            # Use the retrieve_assistants_info function from utils.py
            assistants_info = retrieve_assistants_info()

            # Pass the list of assistants to the template
            return render(request, 'parodynews/assistant_detail.html', {'assistant': assistant, 'openai_assistant': my_assistant, 'assistants_info': assistants_info})
    else:
        form = AssistantForm()
    return render(request, 'parodynews/create_assistant.html', {'form': form})

# New view function to list assistants

def list_assistants(request):
    # Initialize the OpenAI client
    client = OpenAI()

    # Retrieve the list of assistants
    assistants_info = retrieve_assistants_info()

    # Pass the list of assistants to a template
    return render(request, 'parodynews/assistant_detail.html', {'assistants_info': assistants_info})

from django.shortcuts import redirect
from django.contrib import messages
from .utils import delete_assistant

def delete_assistant(request, assistant_id):
    # Call the delete function from utils.py
    response_message = delete_assistant(assistant_id)
    # Optionally, add a success message
    messages.success(request, response_message)
    # Redirect to the list of assistants or another appropriate page
    return redirect('list_assistants')

