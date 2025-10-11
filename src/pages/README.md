
# pages Directory

## Purpose
This directory contains the Jekyll static site generator configuration and content for the publication site component of the parody news generator. It serves as a separate publication system that can display generated content as a static website, complementing the Django web application.

## Contents
- `_about/`: Jekyll about pages and site information
- `_config.yml`: Main Jekyll configuration file with site settings, theme, and build options
- `_config_dev.yml`: Development-specific Jekyll configuration overrides
- `_docs/`: Documentation pages for the Jekyll site
- `_posts/`: Jekyll blog posts and articles (markdown files for generated parody news content)
- `Gemfile`: Ruby gem dependencies for Jekyll build system
- `Gemfile.lock`: Locked gem versions for reproducible builds

## Usage
The Jekyll site can be built and served for publication:

```bash
# Install Jekyll dependencies
bundle install

# Serve development site
bundle exec jekyll serve --config _config.yml,_config_dev.yml

# Build production site
bundle exec jekyll build

# Using Docker (as referenced in main README)
docker compose up -d  # Includes Jekyll on port 4002
```

Key features:
- Static site generation from markdown content
- Theme: "zer0-mistakes" remote theme
- Integration with parody news content from Django app
- Separate publication pipeline for generated articles
- Configurable for development and production environments

## Container Configuration
Jekyll site is containerized alongside Django:
- Runs on port 4002 in Docker compose setup
- Built during container startup
- Serves static files for publication
- Mounts source files for development with live reload

## Related Paths
- Incoming: Receives generated content from Django parodynews app for publication
- Outgoing: Serves static website for public consumption of parody news articles
