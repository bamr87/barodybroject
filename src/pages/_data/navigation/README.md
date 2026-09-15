
# navigation Directory

## Purpose
This directory contains Jekyll navigation data files that define the site's menu structure, navigation links, and page organization for the parody news generator's publication site. These YAML files control how users navigate through different sections of the Jekyll-powered blog and documentation.

## Contents
- `about.yml`: Navigation structure for about pages and project documentation sections
- `main.yml`: Primary site navigation including main menu items, header links, and footer navigation
- `posts.yml`: Blog post navigation including category organization, archive links, and post pagination

## Usage
Navigation files are loaded by Jekyll templates and layouts:

```yaml
# main.yml - a list of entries, each optionally carrying `sublinks`
- title: News
  url: /posts
  sublinks:
    - title: Pages
      url: /pages
- title: About
  url: /about/
  sublinks:
    - title: Config
      url: /about/config
```

Navigation features:
- **Hierarchical Menus**: Support for multi-level navigation with submenus
- **Responsive Design**: Mobile-friendly navigation that adapts to screen size
- **Category Organization**: Logical grouping of content by topic and type
- **Custom URLs**: Flexible URL structure for pages and posts
- **Dynamic Content**: Navigation adapts to available content and categories

## Container Configuration
Navigation data is processed during Jekyll site building:
- YAML files loaded as site data during build process
- Static navigation generated for fast loading
- Responsive navigation components for container viewports
- SEO-friendly URL structure and site organization

## Related Paths
- Incoming: Used by Jekyll templates and layouts to generate site navigation
- Outgoing: Provides navigation structure for publication site user interface
