
# parodynews Directory

## Purpose
This directory contains Django templates specific to the parodynews application functionality. These templates handle the presentation of AI-generated content, OpenAI assistant interactions, content management interfaces, and the core parody news generation workflow.

## Contents
- `_markdown_field.html`: Partial rendering one Markdown-bearing form field — HTML for viewing, raw source only where the field is editable. Included by `content_detail.html` for the fields named in `ContentItemForm.markdown_fields`. Read-only fields render with no editor in the DOM at all, so their source can never be revealed.
- `assistant_detail.html`: Template for displaying individual OpenAI assistant details and configuration
- `assistant_group_detail.html`: Template for managing groups of assistants and their collective functionality
- `content_detail.html`: Template for displaying detailed view of generated parody news content
- `content_processing.html`: Template for the content generation interface and AI processing workflow
- `index.html`: Main parodynews application landing page and navigation
- `message_detail.html`: Template for displaying OpenAI conversation messages and interactions
- `pages_post_detail.html`: Template for detailed view of published posts and articles
- `thread_detail.html`: Template for displaying conversation threads with AI assistants

## Usage
These templates are rendered by parodynews application views:

```python
# In parodynews/views/content.py
def content_detail(request, content_id):
    return render(request, 'parodynews/content_detail.html', context)

def content_processing(request):
    return render(request, 'parodynews/content_processing.html', context)

# In parodynews/views/assistants.py
def assistant_detail(request, assistant_id):
    return render(request, 'parodynews/assistant_detail.html', context)
```

### Markdown rendering

Markdown is rendered **server-side, in exactly one place**:
`parodynews.utils.markdown.render_markdown`, which delegates to
`django-markdownify`'s `|markdownify` filter (bleach-sanitized). The templates
apply the filter directly; `content_detail.js` re-renders a field on blur by
POSTing to the `markdown_preview` view, which calls the same function.

Do **not** add a client-side Markdown library. It would bypass that sanitizer
and inject unsanitized HTML into the DOM — a stored-XSS path in an app whose
content is AI-generated and user-editable — and it would render the same content
differently from every other page. `test_markdown_rendering.py` asserts both.

Do not append `|safe` after `|markdownify`: the filter already returns a
sanitized `SafeString`, so `|safe` is a no-op that reads like a deliberate
escape-hatch.

Template features:
- **Content Generation Interface**: Forms and controls for AI content creation
- **Assistant Management**: Configuration and interaction with OpenAI assistants
- **Content Display**: Formatted presentation of generated parody news
- **Message Threading**: Conversation flow with AI assistants

## Container Configuration
Templates are served through Django's template system:
- Inherit from base templates for consistent layout
- Include Bootstrap and custom CSS for responsive design
- JavaScript integration for dynamic AI interaction
- Real-time updates during content generation process

## Related Paths
- Incoming: Rendered by parodynews Django views in response to user requests
- Outgoing: Generates HTML interfaces for parody news generation and management
