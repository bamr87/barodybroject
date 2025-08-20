
# parodynews Directory

## Purpose
This directory contains Django templates specific to the parodynews application functionality. These templates handle the presentation of AI-generated content, OpenAI assistant interactions, content management interfaces, and the core parody news generation workflow.

## Contents
- `assistant_detail.html`: Template for displaying individual OpenAI assistant details and configuration
- `assistant_group_detail.html`: Template for managing groups of assistants and their collective functionality
- `cms.html`: Content Management System interface template for content editing and management
- `content_detail.html`: Template for displaying detailed view of generated parody news content
- `content_processing.html`: Template for the content generation interface and AI processing workflow
- `index.html`: Main parodynews application landing page and navigation
- `message_detail.html`: Template for displaying OpenAI conversation messages and interactions
- `pages_post_detail.html`: Template for detailed view of published posts and articles
- `thread_detail.html`: Template for displaying conversation threads with AI assistants

## Usage
These templates are rendered by parodynews application views:

```python
# In parodynews/views.py
def content_detail(request, content_id):
    return render(request, 'parodynews/content_detail.html', context)

def content_processing(request):
    return render(request, 'parodynews/content_processing.html', context)

def assistant_detail(request, assistant_id):
    return render(request, 'parodynews/assistant_detail.html', context)
```

Template features:
- **Content Generation Interface**: Forms and controls for AI content creation
- **Assistant Management**: Configuration and interaction with OpenAI assistants
- **Content Display**: Formatted presentation of generated parody news
- **Message Threading**: Conversation flow with AI assistants
- **CMS Integration**: Content editing and publishing workflow

## Container Configuration
Templates are served through Django's template system:
- Inherit from base templates for consistent layout
- Include Bootstrap and custom CSS for responsive design
- JavaScript integration for dynamic AI interaction
- Real-time updates during content generation process

## Related Paths
- Incoming: Rendered by parodynews Django views in response to user requests
- Outgoing: Generates HTML interfaces for parody news generation and management
