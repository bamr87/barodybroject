
# .vscode Directory

## Purpose
This directory contains Visual Studio Code workspace configuration for the barodybroject. It provides IDE settings, debugging configurations, build tasks, and extension recommendations that optimize the development experience for Django applications with OpenAI integration.

## Contents
- `launch.json`: Debug configuration for Python/Django debugging with breakpoints and variable inspection
- `settings.json`: Workspace-specific settings for Python, Django, and development tools
- `tasks.json`: Build and development tasks for running servers, tests, and deployment commands

## Usage
VS Code automatically loads these configurations when opening the project:

```json
// Example debug configuration in launch.json
{
  "name": "Django Server",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/src/manage.py",
  "args": ["runserver", "0.0.0.0:8000"],
  "django": true
}
```

Development features:
- **Integrated Debugging**: Set breakpoints in Django views and models
- **Code Formatting**: Automatic Python code formatting with Black
- **Linting**: Real-time error detection with flake8 and pylint
- **IntelliSense**: Smart code completion for Django and Python
- **Test Integration**: Run and debug unit tests within VS Code
- **Git Integration**: Built-in Git workflow and diff visualization

## Container Configuration
VS Code settings are container-aware:
- Configured for development container environment
- Python interpreter path points to container Python
- Database connection settings for containerized PostgreSQL
- Port forwarding configuration for development servers

## Related Paths
- Incoming: Used by VS Code IDE when editing project files
- Outgoing: Provides development environment configuration for efficient Django development
