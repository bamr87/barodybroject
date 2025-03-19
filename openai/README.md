# OpenAI GitHub Issue Automation

This directory contains scripts and dependencies to automatically generate structured functional requirements from feature requests using OpenAI's GPT-4-turbo API.

## Files

- **`create_sub_issue.py`**:  
  Python script to automate the creation of structured functional requirements based on original feature requests.

- **`requirements.txt`**:  
  Lists Python dependencies required for running the script.

## Setup Instructions

1. **Create GitHub Secrets**:
   - `OPENAI_API_KEY`
   - `OPENAI_ORG_ID`

2. **Install Dependencies**:
   ```bash
   pip install -r openai/requirements.txt