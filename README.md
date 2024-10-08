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

Visit [http://localhost:8000](http://localhost:8000) in your web browser to view the application.

### Run the Publication Site (Jekyll)

```sh
# build the docker image based on the Dockerfile
docker build -t test1 .
```

```sh
# run the docker image and mount the local directory to the container and open a bash shell
docker run -d -p 4002:4002 -v ${GITHOME}/test1:/app --name test1_container test1
```

```sh


### Screenshots

![alt text](/assets/images/home.png)

![alt text](assets/images/roles.png)

![alt text](assets/images/content.png)

![alt text](assets/images/assistants.png)

![alt text](assets/images/messages.png)

![alt text](assets/images/threads.png)