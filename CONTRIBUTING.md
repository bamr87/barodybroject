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

### Documentation & Change Management

This project maintains a comprehensive changelog documentation system to track all changes consistently. Before contributing, please familiarize yourself with our change documentation process:

- **Main Project Changelog**: [docs/changelog/CHANGELOG.md](docs/changelog/CHANGELOG.md)
- **Change Documentation Guidelines**: [docs/changelog/CONTRIBUTING_CHANGES.md](docs/changelog/CONTRIBUTING_CHANGES.md)
- **Change Templates**: [docs/changelog/templates/](docs/changelog/templates/) - Use these for documenting your contributions

### Types of Changes We Track

- **Features**: New functionality, enhancements, or capabilities ([template](docs/changelog/templates/feature-template.md))
- **Bug Fixes**: Corrections to existing functionality ([template](docs/changelog/templates/bugfix-template.md))
- **Improvements**: Optimizations, refactoring, or code quality enhancements ([template](docs/changelog/templates/improvement-template.md))
- **Security**: Security-related fixes or enhancements ([template](docs/changelog/templates/security-template.md))
- **Breaking Changes**: Changes that break backward compatibility ([template](docs/changelog/templates/breaking-template.md))

### Fork the Repository

1. Navigate to the [Parody News Generator repository](https://github.com/bamr87/barodybroject).
2. Click the "Fork" button in the upper right corner of the page to create a copy of the repository in your GitHub account.

### Set Up a Local Development Environment

1. **Clone the Repository**

   ```sh
   git clone https://github.com/bamr87/barodybroject.git
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

2. Make your changes and test them thoroughly

3. Document your changes using our changelog system:
   - Choose the appropriate template from [docs/changelog/templates/](docs/changelog/templates/)
   - Create documentation in the appropriate directory under [docs/changelog/](docs/changelog/)
   - Follow the guidelines in [CONTRIBUTING_CHANGES.md](docs/changelog/CONTRIBUTING_CHANGES.md)

4. Commit your changes with a descriptive commit message:

   ```sh
   git add .
   git commit -m "Add new feature: [brief description]"
   ```

5. Push your changes to your forked repository:

   ```sh
   git push origin my-feature-branch
   ```

### Submitting a Pull Request

1. Navigate to the original repository and click the "New pull request" button.
2. Select your branch from the "compare" dropdown.
3. Provide a descriptive title and detailed description of your changes.
4. **Include references to your change documentation** in the pull request description.
5. Link to any relevant change documents you created in the `docs/changelog/` directory.
6. Click "Create pull request" to submit your changes for review.

### Pull Request Review Process

All pull requests will be reviewed for:
- Code quality and functionality
- Adherence to project standards
- Completeness of change documentation
- Test coverage and validation

Please refer to our [change contribution guidelines](docs/changelog/CONTRIBUTING_CHANGES.md) for detailed review criteria.

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
