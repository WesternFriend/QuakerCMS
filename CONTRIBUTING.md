# Contributing to QuakerCMS

Thank you for your interest in contributing to QuakerCMS! This guide will help you set up your development environment and get started.

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/WesternFriend/QuakerCMS.git
cd QuakerCMS
```

### 2. Install uv (if not already installed)

#### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or install via pip:
```bash
pip install uv
```

### 3. Create and Sync Virtual Environment

Create a virtual environment and install all dependencies:

```bash
uv sync
```

This command will:
- Create a virtual environment in `.venv/`
- Install all project dependencies
- Install development dependencies (like `ruff` for linting) automatically

### 4. Activate the Virtual Environment

#### macOS/Linux
```bash
source .venv/bin/activate
```

#### Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt)
```cmd
.venv\Scripts\activate.bat
```

### 5. Navigate to the Django Project Directory

```bash
cd src
```

### 6. Run Database Migrations

Set up the database by running the initial migrations:

```bash
python manage.py migrate
```

### 7. Create a Superuser Account

Create an admin account to access the Wagtail admin interface:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account with username, email, and password.

### 8. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

### 9. Access the Site

Once the server is running, you can access:

- **Main site**: http://127.0.0.1:8000/
- **Wagtail admin**: http://127.0.0.1:8000/admin/

Log in to the admin interface using the superuser credentials you created in step 7.

## Development Workflow

### Code Quality

This project uses `ruff` for code linting and formatting, along with `pre-commit` hooks to automatically maintain code quality.

#### Pre-commit Hooks (Recommended)

Pre-commit hooks will automatically run code quality checks before each commit:

```bash
# Install pre-commit hooks (one-time setup)
uv run pre-commit install

# Manually run hooks on all files (optional)
uv run pre-commit run --all-files
```

Once installed, the hooks will run automatically on staged files before each commit.

#### Manual Code Quality Checks

You can also run code quality checks manually:

```bash
# Run linting and automatically fix issues
uv run ruff check --fix .

# Run formatting
uv run ruff format .
```

You can also run linting without auto-fixing to see what issues exist:

```bash
# Run linting without auto-fix (view-only)
uv run ruff check .
```

### Adding Dependencies

To add new dependencies:

```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Running Tests

```bash
python manage.py test
```

### Updating Dependencies

To update all dependencies to their latest compatible versions:

```bash
uv sync --upgrade
```

## Project Structure

```
QuakerCMS/
├── src/                    # Django project root
│   ├── core/              # Main Django app with settings
│   ├── home/              # Home page app
│   ├── search/            # Search functionality
│   └── manage.py          # Django management script
├── docs/                  # Documentation
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── pyproject.toml         # Project configuration and dependencies
├── requirements.txt       # Generated requirements file (for deployment)
├── uv.lock               # Locked dependency versions
└── README.md             # Project overview
```

## Making Changes

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the project's coding standards

3. Test your changes thoroughly

4. Run linting and formatting:
   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   ```

5. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add descriptive commit message"
   ```

6. Push your branch and create a pull request

## Getting Help

If you encounter any issues or have questions:

1. Check the existing issues on GitHub
2. Create a new issue with detailed information about your problem
3. Reach out to the maintainers

## License

By contributing to QuakerCMS, you agree that your contributions will be licensed under the AGPL-3.0-or-later license.
