# Parody News Generator

## Description

Django application that integrates with OpenAI to generate content with the help of assistants.

## Features

- **User Authentication**: Supports standard user registration, login, logout, and password management.
- **Dynamic Content Management**: Admin interface for managing content, users, and site settings.
- **RESTful API**: Provides a RESTful API for interacting with the application data programmatically.
- **Responsive Design**: Utilizes Bootstrap for a responsive design that adapts to various screen sizes.
- **Blog Module**: Includes a blog module with categories, tags, and a commenting system.
- **Search Functionality**: Integrated search functionality for finding content within the site.
- **Security Features**: Implements Django's built-in security features to protect against XSS, CSRF, SQL Injection, and more.

## Powered By

- **Django**: High-level Python Web framework that encourages rapid development and clean, pragmatic design.
- **OpenAI**: API for accessing new AI models developed by OpenAI.
- **Bootstrap**: Front-end open source toolkit for developing with HTML, CSS, and JS.
<!-- - **Tailwind CSS**: Utility-first CSS framework packed with classes like flex, pt-4, text-center, and rotate-90 that can be composed to build any design, directly in your markup. -->
- **SQLite**: Self-contained, serverless, zero-configuration, transactional SQL database engine.
<!-- - **Sphinx**: Python documentation generator that converts reStructuredText files into HTML websites and PDFs. -->
- **Docker**: Open platform for developing, shipping, and running applications.
<!-- - **React**: JavaScript library for building user interfaces. -->
- **Jekyll**: Simple, blog-aware static site generator for personal, project, or organization sites.

## Tools

<!-- - **Selenium**: Portable framework for testing web applications. -->

## Installation

Follow these steps to set up a development environment for this Django project:

### Prerequisites

- Github CLI
- Python 3.8 or higher
- pip (Python package manager)
- Virtualenv (optional but recommended for creating isolated Python environments)

### Setup

[zer0](https://it-journey.dev/zer0/)

1. **Clone the Repository**

```sh
cd ~/github/
gh repo clone bamr87/barodybroject test1
cd test1
```

```bash
git clone https://github.com/bamr87/barodybroject.git
cd barodybroject
```

2. **Create a Virtual Environment (Optional)**

- For Unix/Linux/Mac:

```bash
python3 -m venv .venvtest1
source .venvtest1/bin/activate
```

- For Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

1. **Install Dependencies**

With your virtual environment activated, install the project dependencies:

```bash
pip install -r requirements.txt
```

2. **Set Up Environment Variables**

Create a `.env` file in the project root directory and add your environment-specific variables. For example:

```plaintext
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///db.sqlite3
```

3. **Database Migrations**

Apply the database migrations to set up your database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create Superuser (Optional)**

To access the Django admin, create a superuser account:

```bash
python manage.py createsuperuser
```

5. **Run the Development Server**

Start the Django development server:

```bash
python manage.py runserver
```

Your project should now be running at [http://localhost:8000](http://localhost:8000).

### Running the Project

After installation, you can run the project locally using:

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) in youπr web browser to view the application.

### Run the Publication Site (Jekyll)

```sh
# build the docker image based on the Dockerfile
docker build -t barody .
```

```sh
# run the docker image and mount the local directory to the container and open a bash shell
docker run -d -p 8000:8000 -p 4002:4002 --env-file .env --name container-barody barody
```


### Screenshots

![alt text](/assets/images/home.png)

![alt text](assets/images/roles.png)

![alt text](assets/images/content.png)

![alt text](assets/images/assistants.png)

![alt text](assets/images/messages.png)

![alt text](assets/images/threads.png)

## Deploy Django Application with PostgreSQL via Azure Container Apps

This project deploys a web application for a space travel agency using Django. The application can be deployed to Azure with Azure Container Apps using the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview).

```sh
# sample site
gh repo clone Azure-Samples/azure-django-postgres-flexible-aca
cd azure-django-postgres-flexible-aca
```

## Opening the project

This project has [Dev Container support](https://code.visualstudio.com/docs/devcontainers/containers), so it will be setup automatically if you open it in Github Codespaces or in local VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

If you're *not* using one of those options for opening the project, then you'll need to:

1. Start up a local PostgreSQL server, create a database for the app, and set the following environment variables according to your database configuration.

```shell
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=<YOUR DATABASE>
export POSTGRES_USERNAME=<YOUR USERNAME>
export POSTGRES_PASSWORD=<YOUR PASSWORD>
```

1. Create a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) and activate it.

```sh
# Create a virtual environment source .venvazure/bin/activate  # Activate the virtual environment
python3 -m venv .venvazure   
source .venvazure/bin/activate
```

2. install postgresql & admin

```sh
brew install postgresql
brew install pgadmin4
```

1. Install production requirements:

```sh
python3 -m pip install -r src/requirements.txt
```

2. Start the PostgreSQL server:

```sh
brew services start postgresql@14
```


1. Apply database migrations and seed initial data:

```sh
python3 src/manage.py migrate
# python3 src/manage.py loaddata src/seed_data.json
```

## Running locally

If you're running the app inside VS Code or GitHub Codespaces, you can use the "Run and Debug" button to start the app.

```sh
python3 src/manage.py runserver 8000
```

### Admin

This app comes with the built-in Django admin interface.

1. Create a superuser:

```
python3 src/manage.py createsuperuser
```

2. Restart the server and navigate to "/admin"

3. Login with the superuser credentials.

## Running tests

1. Install the development requirements:

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium --with-deps
```

2. Run the tests:

```sh
python3 -m pytest
```

## Deployment

This repo is set up for deployment on Azure via Azure Container Apps.

Steps for deployment:

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/) and create an Azure Subscription.
2. Install the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd). (If you open this repository in Codespaces or with the VS Code Dev Containers extension, that part will be done for you.)
3. Login to Azure:

```shell
azd auth login
```

4. Provision and deploy all the resources:

```shell
azd up
```

    It will prompt you to provide an `azd` environment name (like "myapp"), select a subscription from your Azure account, and select a location (like "eastus"). Then it will provision the resources in your account and deploy the latest code. If you get an error with deployment, changing the location can help, as there may be availability constraints for some of the resources.

5. When `azd` has finished deploying, you'll see an endpoint URI in the command output. Visit that URI, and you should see the front page of the app! 🎉

6. When you've made any changes to the app code, you can just run:

```shell
azd deploy
```

### CI/CD pipeline

This project includes a Github workflow for deploying the resources to Azure
on every push to main. That workflow requires several Azure-related authentication secrets
to be stored as Github action secrets. To set that up, run:

```shell
azd pipeline config
```

