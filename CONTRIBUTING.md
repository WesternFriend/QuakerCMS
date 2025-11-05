# Contributing to QuakerCMS

Thank you for your interest in contributing to QuakerCMS! This guide will help you set up your development environment and get started.

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

## Development Environment Setup

### Option 1: Local Development (Recommended)

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

Alternatively, install via pip:
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

### 9. Install Tailwind CSS Dependencies

QuakerCMS uses Tailwind CSS with DaisyUI for styling. You need to install the Node.js dependencies:

```bash
# Navigate to the Tailwind source directory
cd theme/static_src

# Install npm dependencies
npm install

# Return to the src directory
cd ../..
```

### 10. Set Up Test Navigation Content (Optional but Recommended)

To quickly set up sample pages and navigation menu for development:

```bash
# This creates test pages (About, Programs, Contact) and configures the navigation menu
python manage.py scaffold_navbar_content
```

This command creates:
- **About** page (top-level)
- **Programs** page with a dropdown containing:
  - Programs overview
  - Adult Education
  - Youth Programs
- **FGC Website** external link
- **Contact** page (top-level)

To reset and recreate the test content:

```bash
python manage.py scaffold_navbar_content --delete
```

### 11. Access the Site

Once the server is running, you can access:

- **Main site**: <http://127.0.0.1:8000/>
- **Wagtail admin**: <http://127.0.0.1:8000/admin/>

Log in to the admin interface using the superuser credentials you created in step 7.

### Option 2: Docker Development

For a quick setup using Docker:

```bash
# Clone the repository
git clone https://github.com/WesternFriend/QuakerCMS.git
cd QuakerCMS

# Build and run with Docker Compose
docker-compose up --build

# In another terminal, create a superuser
docker-compose exec web python manage.py createsuperuser
```

Access the site at <http://localhost:8000/>

## Development Workflow

### Running Development Servers

QuakerCMS requires **two development servers** running simultaneously:

1. **Django development server** - Serves the application
2. **Tailwind CSS watcher** - Automatically rebuilds CSS when files change

#### Option A: Two Terminal Windows (Recommended)

**Terminal 1 - Django Server:**
```bash
cd src
python manage.py runserver
```

**Terminal 2 - Tailwind CSS Watcher:**
```bash
cd src/theme/static_src
npm run dev
```

This setup provides:
- ✅ Auto-reload when Python/template files change (Django)
- ✅ Auto-rebuild CSS when templates/classes change (Tailwind)
- ✅ Live browser refresh with django-browser-reload (in DEBUG mode)

#### Option B: Single Command (Requires Honcho)

If you have `honcho` installed (part of django-tailwind optional dependencies):

```bash
cd src
python manage.py tailwind dev
```

This runs both servers together, but requires the `honcho` package.

### Navigation Menu Configuration

The navigation menu is configured in **Wagtail Admin → Settings → Navigation Menu**.

#### Quick Setup with Test Data

Use the scaffold command to quickly set up test pages and navigation:

```bash
# First time setup or when you need fresh test data
python manage.py scaffold_navbar_content

# Reset existing test data and recreate
python manage.py scaffold_navbar_content --delete

# Create pages only (skip navigation menu configuration)
python manage.py scaffold_navbar_content --skip-menu
```

#### Manual Configuration

To manually configure the navigation menu:

1. Go to **Wagtail Admin** (<http://127.0.0.1:8000/admin/>)
2. Navigate to **Settings → Navigation Menu**
3. Add menu items using the StreamField:
   - **Page Link** - Links to Wagtail pages
   - **External Link** - Links to external URLs
   - **Dropdown** - Creates a dropdown with nested items (max 2 levels)

The navigation system automatically:
- Shows the current page with `aria-current="page"`
- Links to translated versions in multilingual sites
- Provides mobile-responsive drawer navigation
- Ensures WCAG 2.1 AA accessibility compliance

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
# Run tests with Django test runner
python manage.py test

# Run tests with pytest (alternative)
uv run pytest

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML coverage report
```

Note: All tests also run automatically in our GitHub Actions CI pipeline when you create a pull request.

### Updating Dependencies

To update all dependencies to their latest compatible versions:

```bash
uv sync --upgrade
```

## Project Structure

```text
QuakerCMS/
├── .github/
│   ├── ISSUE_TEMPLATE/    # Issue templates for bugs, features, questions
│   ├── workflows/
│   │   └── ci.yml         # GitHub Actions CI pipeline
│   ├── dependabot.yml    # Automated dependency updates
│   └── pull_request_template.md # PR template
├── src/                    # Django project root
│   ├── core/              # Main Django app with settings
│   │   ├── settings/      # Settings split by environment (base, dev, production)
│   │   ├── constants.py   # Shared constants (e.g., language codes)
│   │   └── templates/     # Core templates (base.html, 404, 500)
│   ├── home/              # Home page app
│   ├── content/           # General content pages with StreamField
│   ├── navigation/        # Navigation menu system
│   │   ├── blocks.py      # StreamField blocks for menu items
│   │   ├── models.py      # NavigationMenuSetting model
│   │   ├── templatetags/  # Template tags for rendering navigation
│   │   ├── templates/     # Navigation template
│   │   ├── management/    # Management commands (scaffold_navbar_content)
│   │   └── README.md      # Navigation system documentation
│   ├── locales/           # Internationalization settings
│   ├── search/            # Search functionality
│   ├── theme/             # Tailwind CSS theme
│   │   └── static_src/    # Tailwind source files
│   │       ├── src/
│   │       │   └── styles.css  # Tailwind configuration
│   │       ├── package.json    # Node.js dependencies
│   │       └── postcss.config.js
│   └── manage.py          # Django management script
├── docs/                  # Documentation
├── specs/                 # Feature specifications and planning
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── CHANGELOG.md           # Project changelog
├── docker-compose.yml     # Docker development environment
├── Dockerfile             # Docker configuration
├── pyproject.toml         # Project configuration and dependencies
├── requirements.txt       # Generated requirements file (for deployment)
├── SECURITY.md            # Security policy
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

## Continuous Integration

The project uses GitHub Actions for continuous integration. When you create a pull request, the CI pipeline will automatically:

- **Test Matrix**: Run tests on Python 3.12 and 3.13
- **Code Quality**: Run pre-commit hooks including ruff linting and formatting
- **Django Checks**: Run Django system checks and security checks
- **Database**: Test database migrations

All checks must pass before a pull request can be merged. You can view the status of these checks on your pull request page.

## Troubleshooting

### Tailwind CSS Not Working / Styles Missing

**Problem**: Navigation menu or other components appear unstyled.

**Solution**: Make sure the Tailwind CSS watcher is running:

```bash
cd src/theme/static_src
npm run dev
```

If styles are still missing:

```bash
# Rebuild Tailwind CSS in production mode
npm run build

# Then hard refresh your browser (Cmd+Shift+R on macOS, Ctrl+Shift+R on Windows/Linux)
```

### "Skip to main content" Link Always Visible

**Problem**: The accessibility skip link appears all the time instead of only on focus.

**Solution**: The Tailwind CSS watcher needs to be running. The `sr-only` utility class requires compiled CSS:

```bash
cd src/theme/static_src
npm run dev
```

### Navigation Menu Not Appearing

**Problem**: No navigation menu shows on pages.

**Solutions**:

1. **Check if navigation menu is configured**:
   - Go to Wagtail Admin → Settings → Navigation Menu
   - Add at least one menu item

2. **Use the scaffold command**:
   ```bash
   cd src
   python manage.py scaffold_navbar_content
   ```

3. **Check if pages exist**: The menu only shows published pages.

### Page Tree Errors When Creating Pages

**Problem**: Error like `'NoneType' object has no attribute '_inc_path'` when creating pages.

**Solution**: Fix the page tree structure:

```bash
cd src
python manage.py fixtree
```

The `scaffold_navbar_content --delete` command automatically runs this after deletion.

### Database Migration Issues

**Problem**: Errors when running `python manage.py migrate`.

**Solution**:

```bash
# Check for migration conflicts
python manage.py makemigrations --check

# If there are unapplied migrations, apply them
python manage.py migrate

# If you have migration conflicts, you may need to merge migrations
python manage.py makemigrations --merge
```

### Import Errors / Module Not Found

**Problem**: `ModuleNotFoundError` when running Django commands.

**Solution**: Make sure your virtual environment is activated:

```bash
# Activate the virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Verify Django is installed
python -c "import django; print(django.get_version())"
```

If Django is not installed:

```bash
# Reinstall dependencies
uv sync
```

## Getting Help

If you encounter any issues or have questions:

1. Check the existing issues on GitHub
2. Create a new issue with detailed information about your problem
3. Reach out to the maintainers

## Quick Reference

### Common Commands

```bash
# Start Django development server
cd src
python manage.py runserver

# Start Tailwind CSS watcher
cd src/theme/static_src
npm run dev

# Create test navigation content
cd src
python manage.py scaffold_navbar_content

# Reset and recreate test content
python manage.py scaffold_navbar_content --delete

# Run tests
cd src
python manage.py test

# Run linting and formatting
uv run ruff check --fix .
uv run ruff format .

# Fix page tree issues
cd src
python manage.py fixtree

# Create database migrations
cd src
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Important URLs

- **Main Site**: <http://127.0.0.1:8000/>
- **Wagtail Admin**: <http://127.0.0.1:8000/admin/>
- **Navigation Menu Settings**: <http://127.0.0.1:8000/admin/settings/navigation/navigationmenusetting/>

### Key Files

- `src/core/settings/base.py` - Main Django settings
- `src/core/constants.py` - Shared constants (language codes, etc.)
- `src/navigation/models.py` - Navigation menu model
- `src/navigation/templatetags/navigation_tags.py` - Navigation rendering logic
- `src/theme/static_src/src/styles.css` - Tailwind CSS configuration
- `pyproject.toml` - Project dependencies and configuration

### Development Tips

1. **Always run both servers** (Django + Tailwind) for development
2. **Use `scaffold_navbar_content`** to quickly set up test pages
3. **Run `fixtree`** if you encounter page tree errors
4. **Hard refresh browser** (Cmd+Shift+R / Ctrl+Shift+R) if CSS changes don't appear
5. **Check pre-commit hooks** run before commits for code quality

## License

By contributing to QuakerCMS, you agree that your contributions will be licensed under the AGPL-3.0-or-later license.
