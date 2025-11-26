==========
Quickstart
==========

Get started with Parodynews in 5 minutes!

After completing :doc:`installation` and :doc:`configuration`, follow these steps
to generate your first piece of content.

Step 1: Access the Admin Interface
===================================

1. Navigate to http://localhost:8000/admin
2. Log in with your superuser credentials
3. You'll see the Django admin dashboard

Step 2: Configure OpenAI Settings
==================================

1. Click on **App configs** in the admin
2. Add or edit the configuration
3. Enter your OpenAI API key
4. Save the configuration

Step 3: Create an Assistant
============================

1. Click on **Assistants** in the admin
2. Click **Add assistant**
3. Fill in the details:
   
   * Name: "Parody News Writer"
   * Instructions: "Write satirical news articles about technology"
   * Select a model (e.g., "gpt-4")

4. Click **Save**

Step 4: Generate Content
=========================

1. Navigate to the content generation page
2. Select your assistant
3. Enter a prompt: "Write about AI taking over software development"
4. Click **Generate**
5. Review the generated content

What's Next?
============

* :doc:`first-content` - More detailed content creation guide
* :doc:`../user-guide/assistants` - Learn more about assistants
* :doc:`../user-guide/content-generation` - Advanced content generation
* :doc:`../tutorials/index` - Follow step-by-step tutorials
