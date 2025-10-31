
# usersessions Directory

## Purpose
This directory contains Django templates for managing user sessions in the parody news generator application. It provides functionality for users to view and manage their active sessions, including the ability to sign out of other sessions for security purposes.

## Contents
- `usersession_list.html`: Main template for displaying user session management interface with session details and sign-out functionality
- `messages/`: Subdirectory containing message templates for session-related user feedback
- `base_manage.html`: Base template that extends the allauth management layout for session management pages

## Usage
These templates are used when users access the session management functionality:

```html
<!-- Example of session list display -->
{% extends "usersessions/base_manage.html" %}
{% load allauth %}
{% load i18n %}

<!-- Shows table of active sessions with details like:
- Session start time
- IP address 
- Browser information
- Last seen timestamp
- Current session indicator
-->
```

Template features:
- **Session Display**: Shows all active user sessions in a structured table format
- **Security Management**: Allows users to sign out of other sessions for security
- **Responsive Design**: Mobile-friendly session management interface
- **Internationalization**: Supports multiple languages through Django i18n
- **User Agent Detection**: Displays browser and device information for each session

## Container Configuration
Templates are served through the Django application container:
- Rendered server-side using Django template engine
- Integrated with allauth session management system
- Styled with responsive CSS for mobile and desktop viewing
- Supports real-time session status updates

## Related Paths
- Incoming: Accessed through user account management, security settings, and session monitoring requests
- Outgoing: Integrates with Django allauth authentication system and user session management backend
