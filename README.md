# Parody News Generator

## Description

Django application integrated with OpenAI to generate content with the help of assistants.

<!-- TODO: add Django CMS functionality -->

### Features

- **User Authentication**: Supports standard user registration, login, logout, and password management.
- **Dynamic Content Management**: Admin interface for managing content, users, and site settings.
- **RESTful API**: Provides a RESTful API for interacting with the application data programmatically.
- **Responsive Design**: Utilizes Bootstrap for a responsive design that adapts to various screen sizes.
- **Blog Module**: Includes a blog module with categories, tags, and a commenting system.
- **Search Functionality**: Integrated search functionality for finding content within the site.
- **Security Features**: Implements Django's built-in security features to protect against XSS, CSRF, SQL Injection, and more.

### New or Updated Features

- **Dynamic Form Support**: Added a reusable Django `DynamicFieldsMixin` and supporting JavaScript file for automatically updating form fields via AJAX.
- **CMS Integration**: Extended `urls.py` to include Django CMS routes under the root URL.
- **AWS App Runner Configuration**: Added an `apprunner.yaml` to streamline build and deployment steps for AWS.
- **Jekyll Config**: Included development and production config overrides and YAML files for advanced static site generation needs.
- **Enhanced Navigation**: Added or updated YAML data files under `_data/navigation` and `_data/ui-text` for easier menu and UI text management.
- **GitHub Automation**: Prepared scripts inside `githubai` directory for AI-assisted GitHub issue handling and README updates.r

### Powered By

- **Django**: High-level Python Web framework that encourages rapid development and clean, pragmatic design.
<!-- - Django CMS: Open-source content management system based on the Django web framework. -->
- **OpenAI**: API for accessing new AI models developed by OpenAI.
- **Bootstrap**: Front-end open source toolkit for developing with HTML, CSS, and JS.
<!-- - **Tailwind CSS**: Utility-first CSS framework packed with classes like flex, pt-4, text-center, and rotate-90 that can be composed to build any design, directly in your markup. -->
- **PostgreSQL**: Powerful, open-source object-relational database system.
- **SQLite**: Self-contained, serverless, zero-configuration, transactional SQL database engine.
- **Sphinx**: Python documentation generator that converts reStructuredText files into HTML websites and PDFs.
- **Docker**: Open platform for developing, shipping, and running applications.
<!-- - **React**: JavaScript library for building user interfaces. -->
- **Jekyll**: Simple, blog-aware static site generator for personal, project, or organization sites.

### Tools

- **Git**: Distributed version control system for tracking changes in source code during software development.
- **Github**: Leading platform for hosting and collaborating on Git repositories.
- **VS Code**: Lightweight but powerful source code editor that runs on your desktop.
- **Docker Compose**: Tool for defining and running multi-container Docker applications.
- **Azure Container Apps**: Service for deploying and scaling containerized applications in the cloud.
- **Azure Developer CLI**: Command-line interface for managing Azure resources.

<!-- - **Selenium**: Portable framework for testing web applications. -->

## Installation

Follow these steps to set up a development environment for this Django project:

### Prerequisites

- Github CLI
- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (optional but recommended for creating isolated Python environments)

### Setup

[zer0](https://it-journey.dev/zer0/)

0. Set naming parameters

```sh
GH_USER=bamr87
GH_REPO=barodybroject
GH_TEST_REPO=barodybroject-test-4
GH_HOME=~/github
GH_REPO_DIR=${GH_HOME}/${GH_TEST_REPO}
PY_VENV=.venv${GH_TEST_REPO}
```


1. **Clone the Repository**

```sh
cd $GH_HOME
gh repo clone bamr87/barodybroject $GH_REPO_DIR
cd $GH_REPO_DIR
```

```bash
# Or clone the repository using the git command
cd $GH_HOME
git clone https://github.com/bamr87/barodybroject.git
cd $GH_REPO_DIR
```

2. **Create a Virtual Environment (Optional)**

- For Unix/Linux/Mac:

```bash
python3 -m venv $PY_VENV
source $PY_VENV/bin/activate
```

- For Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

1. **Install Dependencies**

With your virtual environment activated, install the project dependencies:

```bash
pip install -r requirements-dev.txt
```

2. **Set Up Environment Variables**

Create a `.env` file in the project root directory and add your environment-specific variables. For example:

```sh
cd $GH_REPO_DIR
touch .env
echo "CONTAINER_APP_NAME=${GH_TEST_REPO}" >> .env
echo "CONTAINER_APP_ENV_DNS_SUFFIX=localhost" >> .env
echo "DEBUG=True" >> .env
echo "SECRET_KEY=your_secret_key" >> .env
echo "DATABASE_URL=sqlite:///db.sqlite3" >> .env
```

or manually create the `.env` file and add the following environment variables:

```plaintext
CONTAINER_APP_NAME=${GH_TEST_REPO}
CONTAINER_APP_ENV_DNS_SUFFIX=localhost
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///db.sqlite3
```

3. **Database Migrations**

Apply the database migrations to set up your database schema:

```bash
cd src
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
docker compose build -t $GH_REPO .
```

```sh
# run the docker image and mount the local directory to the container and open a bash shell
# docker run -d -p 8000:8000 -p 4002:4002 --env-file .env --name container-barody barody

docker compose up -d

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
azd auth login
azd init
azd up
```

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
export DB_HOST=localhost
export POSTGRES_PORT=5432
export DB_NAME=<YOUR DATABASE>
export DB_USERNAME=<YOUR USERNAME>
export DB_PASSWORD=<YOUR PASSWORD>
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

## Documentation

Barodybroject includes comprehensive documentation built with Sphinx.

### Building Documentation

To build the documentation locally:

```bash
# Install development dependencies (includes Sphinx)
pip install -r requirements-dev.txt

# Build HTML documentation
cd docs
make html

# Or use the build script
chmod +x scripts/build_docs.sh
./scripts/build_docs.sh
```

The generated documentation will be available in `docs/build/html/index.html`.

### Documentation Features

- **API Documentation**: Automatically generated from docstrings
- **User Guides**: Installation, configuration, and usage instructions
- **Developer Guides**: Contributing guidelines and testing procedures
- **Deployment Guides**: Multiple deployment scenarios and configurations

### Online Documentation

The documentation is automatically built and deployed to GitHub Pages on every push to the main branch.

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

## Development Container Workflow

We've implemented a "push-it-once, pull-it-forever" development container workflow to significantly speed up the development onboarding and environment setup process.

## How It Works

1. **Pre-built Development Image**: Instead of each developer building the Docker image from scratch, we now maintain a pre-built image on Docker Hub that contains all dependencies.

2. **Automatic Image Updates**: When the Dockerfile or requirements change, GitHub Actions automatically builds and publishes a new image to Docker Hub.

3. **Developer Experience**:
   - First-time setup: `docker compose pull && docker compose up`
   - Daily development: Code changes are mounted into the container for instant reload
   - Adding new dependencies: Update `requirements.txt`, push the change, and CI builds a new image

## Manual Image Build (if needed)

You can manually build and push the development container with:

```bash
# From the repository root
docker build -f .devcontainer/Dockerfile_dev \
             -t amrabdel/barody-python:0.1 \
             -t amrabdel/barody-python:latest \
             .

docker login   # enter your Docker Hub credentials
docker push amrabdel/barody-python:0.1
docker push amrabdel/barody-python:latest
```

## Benefits

- **Faster Setup**: New team members can be productive in minutes rather than waiting for lengthy builds
- **Consistent Environment**: Everyone uses exactly the same container image
- **Reduced Resource Usage**: BuildKit caching reduces CI build times and bandwidth usage
- **Hot Reload**: Your local code changes are immediately available inside the container

## Required GitHub Secrets

For the CI workflow to function, add these secrets to your GitHub repository:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: A Personal Access Token from Docker Hub (not your password)

## Troubleshooting

If you encounter issues with the development container:

1. Try pulling the latest image: `docker pull amrabdel/barody-python:latest`
2. Check for any pending changes in the GitHub Actions "Build & publish dev-container" workflow
3. For local debugging, you can temporarily switch back to building locally by changing `image:` to `build:` in the docker-compose file

## Contributing

We welcome contributions from the community! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get involved.
