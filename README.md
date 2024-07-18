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

## Installation

Follow these steps to set up a development environment for this Django project:

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtualenv (optional but recommended for creating isolated Python environments)

### Setup

1. **Clone the Repository**

```bash
git clone https://github.com/bamr87/barodybroject.git
cd barodybroject
```

2. **Create a Virtual Environment (Optional)**

- For Unix/Linux/Mac:

```bash
python3 -m venv venv
source venv/bin/activate
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
```
