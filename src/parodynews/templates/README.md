# templates

## Purpose

What is still server-rendered after the move to React: the SPA shell, the allauth account pages, and a couple of error pages. Application UI lives in [`../../frontend/`](../../frontend/README.md).

## Contents

| Path | What it is |
|---|---|
| `spa/index.html` | The shell the React app mounts into |
| `base.html` | Layout the account pages extend |
| `account/`, `allauth/`, `socialaccount/`, `mfa/`, `usersessions/` | Django-allauth templates |
| `profile.html` | User profile page |
| `footer.html` | Shared footer |
| `429.html` | Rate-limit error page |

## The SPA shell

`spa/index.html` is small but does four specific things:

1. Renders `<div id="root">` for React to mount into.
2. Emits a `csrf` meta tag, which `frontend/src/api/client.ts` reads for write requests.
3. Runs a tiny pre-paint script that applies the stored theme, so a reload in dark mode doesn't flash white.
4. Picks its script tags one of three ways: the Vite dev server when `FRONTEND_DEV_SERVER_URL` is set, the built manifest when `dist/.vite/manifest.json` exists, and a plain message when neither does — so a missing frontend build says so instead of rendering a blank page.

## The account pages make no third-party requests

Worth preserving if you edit `base.html`. These templates used to pull Bootstrap's CSS and JS from a CDN, which meant every login page load depended on jsDelivr being reachable and its certificate validating — and in a restricted network it simply failed.

They now reuse the React bundle's stylesheet, handed to the template by the `site_links` context processor, and load no JavaScript at all. If you add a component here that needs Bootstrap's JS, prefer a CSS-only alternative or move that screen into the SPA.

## Usage

```html
{% extends 'base.html' %}
{% load static %}

{% block content %}
  <!-- page content -->
{% endblock %}
```

## Related paths

- [`../../frontend/README.md`](../../frontend/README.md) — the application UI
- [`../views/spa.py`](../views/spa.py) — reads the Vite manifest and renders the shell
- [`../context_processors.py`](../context_processors.py) — `site_links`, including `frontend_styles`
