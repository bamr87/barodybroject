
# database Directory

## Purpose
This directory contains FrontMatter CMS database files that store content management system data including media assets, taxonomy information, and pinned content items. These JSON files maintain the state and configuration of the FrontMatter extension for managing Jekyll site content through VS Code.

## Contents
- `mediaDb.json`: Database of media assets including images, videos, and documents with metadata and organization information
- `pinnedItemsDb.json`: Database of pinned content items for quick access in the FrontMatter dashboard
- `taxonomyDb.json`: Database of content taxonomy including categories, tags, and content type classifications

## Usage
Database files are automatically managed by FrontMatter CMS:

```json
// Example mediaDb.json structure
{
  "media": [
    {
      "id": "uuid",
      "filename": "screenshot.png",
      "path": "/assets/images/screenshot.png",
      "alt": "Application screenshot",
      "tags": ["ui", "demo"],
      "dateAdded": "2025-08-20T00:00:00Z"
    }
  ]
}

// Example taxonomyDb.json structure
{
  "categories": ["technology", "satire", "business"],
  "tags": ["django", "ai", "openai", "azure"],
  "contentTypes": ["post", "page", "article"]
}
```

Database features:
- **Media Management**: Track and organize images, videos, and documents
- **Content Taxonomy**: Maintain consistent categorization and tagging
- **Quick Access**: Pinned items for frequently used content
- **Metadata Storage**: Rich metadata for content organization
- **Version Control**: Changes tracked through Git for content history

## Container Configuration
Database files are stored locally for VS Code extension:
- JSON format for easy parsing and modification
- Automatic synchronization with file system changes
- Backup and restore through Git version control
- Cross-platform compatibility for development containers

## Related Paths
- Incoming: Updated by FrontMatter CMS extension when managing content
- Outgoing: Used by VS Code extension to display content management interface
