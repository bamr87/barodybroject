# Contributing to Parody News Generator

## Overview of the Project

The Parody News Generator is a Django application integrated with OpenAI to generate content with the help of assistants. The project aims to create a platform for generating parody news articles, providing a fun and engaging way to explore AI-generated content.

## Tech Stack

The project utilizes the following technologies:

- **Django**: High-level Python Web framework that encourages rapid development and clean, pragmatic design.
- **OpenAI**: API for accessing new AI models developed by OpenAI.
- **PostgreSQL**: Powerful, open-source object-relational database system.
- **SQLite**: Self-contained, serverless, zero-configuration, transactional SQL database engine.
- **Docker**: Open platform for developing, shipping, and running applications.
- **Bootstrap**: Front-end open source toolkit for developing with HTML, CSS, and JS.
- **Git**: Distributed version control system for tracking changes in source code during software development.
- **Github**: Leading platform for hosting and collaborating on Git repositories.
- **VS Code**: Lightweight but powerful source code editor that runs on your desktop.
- **Docker Compose**: Tool for defining and running multi-container Docker applications.
- **Azure Container Apps**: Service for deploying and scaling containerized applications in the cloud.
- **Azure Developer CLI**: Command-line interface for managing Azure resources.

## How to Contribute

We welcome contributions from the community! Here are the steps to get started:

### Fork the Repository

1. Navigate to the [Parody News Generator repository](https://github.com/bamr87/barodybroject).
2. Click the "Fork" button in the upper right corner of the page to create a copy of the repository in your GitHub account.

### Set Up a Local Development Environment

1. **Clone the Repository**

   ```sh
   git clone https://github.com/your-username/barodybroject.git
   cd barodybroject
   ```

2. **Create a Virtual Environment**

   - For Unix/Linux/Mac:

     ```sh
     python3 -m venv .venv
     source .venv/bin/activate
     ```

   - For Windows:

     ```sh
     python -m venv venv
     .\venv\Scripts\activate
     ```

3. **Install Dependencies**

   ```sh
   pip install -r requirements-dev.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the project root directory and add your environment-specific variables. For example:

   ```sh
   touch .env
   echo "DEBUG=True" >> .env
   echo "SECRET_KEY=your_secret_key" >> .env
   echo "DATABASE_URL=sqlite:///db.sqlite3" >> .env
   ```

5. **Database Migrations**

   Apply the database migrations to set up your database schema:

   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser (Optional)**

   To access the Django admin, create a superuser account:

   ```sh
   python manage.py createsuperuser
   ```

7. **Run the Development Server**

   Start the Django development server:

   ```sh
   python manage.py runserver
   ```

   Your project should now be running at [http://localhost:8000](http://localhost:8000).

### Making Changes

1. Create a new branch for your changes:

   ```sh
   git checkout -b my-feature-branch
   ```

2. Make your changes and commit them with a descriptive commit message:

   ```sh
   git add .
   git commit -m "Add new feature"
   ```

3. Push your changes to your forked repository:

   ```sh
   git push origin my-feature-branch
   ```

### Submitting a Pull Request

1. Navigate to the original repository and click the "New pull request" button.
2. Select your branch from the "compare" dropdown.
3. Provide a descriptive title and detailed description of your changes.
4. Click "Create pull request" to submit your changes for review.

## Types of Contributions

We welcome various types of contributions, including:

- **Bug Fixes**: Identify and fix bugs in the codebase.
- **Feature Requests**: Suggest and implement new features.
- **Documentation Improvements**: Enhance the project's documentation.
- **Testing**: Write and improve tests to ensure code quality.

## Code of Conduct

We are committed to fostering a welcoming and respectful environment for all contributors. Please read and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

## Contact Information

If you have any questions or need further assistance, please reach out to the maintainers:

- **bamr87**: [bamr87@users.noreply.github.com](mailto:bamr87@users.noreply.github.com)
