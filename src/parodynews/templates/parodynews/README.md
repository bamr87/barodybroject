
# parodynews Directory

## Purpose
This directory contains Django templates specific to the parodynews application functionality. These templates handle the presentation of AI-generated content, OpenAI assistant interactions, content management interfaces, and the core parody news generation workflow.

## Contents
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

Template features:
- **Content Generation Interface**: Forms and controls for AI content creation
- **Assistant Management**: Configuration and interaction with OpenAI assistants
- **Content Display**: Formatted presentation of generated parody news
- **Message Threading**: Conversation flow with AI assistants

## Markdown rendering

Fields that hold Markdown are rendered as HTML wherever they are shown for *reading* rather
than editing, via the `markdownify` filter from `django-markdownify`. Martor handles the
*editing* side and is a separate pipeline — do not route display through it.

| Template | Field | Filter | Notes |
| --- | --- | --- | --- |
| `content_detail.html` | assistant `instructions` | `markdownify:"readonly"` | Display-only field. Rendered into `#instructions-rendered`; a sibling hidden input carries the raw value so the submitted payload is unchanged. `content_detail.js` refreshes both from `instructions_html` / `instructions` when the assistant selection changes. |
| `message_detail.html` | `contentitem.content_text` | `markdownify\|linebreaksbr` | Library defaults. |
| `content_processing.html` | `contentitem.content_text` | `dict_to_text_list\|markdownify\|linebreaksbr` | Library defaults. |

The `readonly` profile is defined in `barodybroject/settings/base.py` (`MARKDOWNIFY`). It
exists because django-markdownify falls back to `bleach.sanitizer.ALLOWED_TAGS` when
unconfigured, and that default set contains no heading, paragraph or `<pre>` tag — an
unprofiled `|markdownify` renders `## Heading` as the bare word `Heading`. The two call sites
marked *library defaults* above are still subject to that and are candidates for the same
treatment; they were left unchanged here to keep the change scoped.

Anything inserted into a rendered block from JavaScript must be sanitised **server-side**
first — never assign raw Markdown or unsanitised HTML to `innerHTML`.

## Container Configuration
Templates are served through Django's template system:
- Inherit from base templates for consistent layout
- Include Bootstrap and custom CSS for responsive design
- JavaScript integration for dynamic AI interaction
- Real-time updates during content generation process

## Related Paths
- Incoming: Rendered by parodynews Django views in response to user requests
- Outgoing: Generates HTML interfaces for parody news generation and management
