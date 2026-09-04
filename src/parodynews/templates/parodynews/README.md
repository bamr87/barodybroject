
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

## List tables

Every list table on these pages is sortable and filterable client-side, via
`assets/js/table_utils.js`. **Never hand-roll a `<th>`** — the sort handler binds to
`th.sortable` while the filter binds to `input.filter`, so a header missing the class
gets a working filter and a dead sort, which looks functional and is not. See
[`../includes/README.md`](../includes/README.md) for the full contract.

| Template | List table | Renders headers via |
| --- | --- | --- |
| `content_detail.html` | Content Listing | `{% render_model_table %}` |
| `content_processing.html` | Messages | `{% render_model_table %}` |
| `pages_post_detail.html` | Posts | `{% render_model_table %}` |
| `assistant_detail.html` | Assistant List | `includes/sortable_header.html` — rows are click-through links |
| `assistant_group_detail.html` | Assistant Groups | `includes/sortable_header.html` — rows are click-through links |
| `message_detail.html` | Messages | `includes/sortable_header.html` — static columns; rows embed assign/delete forms |
| `thread_detail.html` | Thread messages | `includes/sortable_header.html` — rows embed an "Add to Database" form |

The four using `sortable_header.html` cannot use `{% render_model_table %}`: it renders its
first cell as a link and has no way to express row-level click-through, an embedded form,
or a static column, so migrating them would trade a dead sort for lost behaviour.

> **Note on `thread_detail.html`:** no view currently renders it — the `thread_detail` URL
> routes to `ProcessContentView`, which renders `content_processing.html`. Its headers also
> come from the `Thread` model's four `display_fields` while its body renders three fixed
> cells. Both predate this table work; the template is kept contract-compliant, but it
> should be either wired up or deleted.

## Container Configuration
Templates are served through Django's template system:
- Inherit from base templates for consistent layout
- Include Bootstrap and custom CSS for responsive design
- JavaScript integration for dynamic AI interaction
- Real-time updates during content generation process

## Related Paths
- Incoming: Rendered by parodynews Django views in response to user requests
- Outgoing: Generates HTML interfaces for parody news generation and management
