
# .frontmatter Directory

## Purpose
This directory contains FrontMatter CMS configuration and database files. FrontMatter is a Visual Studio Code extension that provides a content management system interface for static sites and Jekyll-based projects, allowing content editors to manage markdown files and frontmatter metadata through a visual interface.

## Contents
- `database/`: FrontMatter CMS database files for content management (has its own README)

## Usage
FrontMatter CMS is integrated with VS Code for content management:

```json
// In .vscode/settings.json
{
  "frontMatter.taxonomy.contentTypes": [{
    "name": "default",
    "pageBundle": false,
    "fields": []
  }]
}
```

Features provided:
- **Visual Content Editor**: WYSIWYG interface for markdown content
- **Frontmatter Management**: GUI for editing YAML frontmatter in markdown files
- **Media Management**: Image and asset organization for Jekyll sites
- **Content Organization**: File and folder structure management
- **Publishing Workflow**: Content review and publishing controls

## Container Configuration
FrontMatter runs as a VS Code extension:
- Operates within the development container environment
- Provides content management for Jekyll static site generation
- Integrates with Git workflow for content versioning
- Supports real-time preview and editing capabilities

## Related Paths
- Incoming: Used by content editors and developers through VS Code
- Outgoing: Manages markdown files in src/pages/ and content directories
