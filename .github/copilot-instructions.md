# QuakerCMS Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-26

## Active Technologies

- Python 3.12+ + Django 5.2+, Wagtail 7.0+, django-tailwind (latest), Node.js/npm (for Tailwind compilation) (001-tailwind-integration)

## Project Structure

```text
src/
tests/
```

## Commands

```bash
# Navigate to source directory
cd src

# Run tests
pytest

# Run linter
ruff check .

# Start development server
python manage.py runserver

# Build Tailwind CSS (run in theme/static_src directory)
cd theme/static_src
npm run dev
```

## Code Style

Python 3.12+: Follow standard conventions

## Recent Changes

- 001-tailwind-integration: Added Python 3.12+ + Django 5.2+, Wagtail 7.0+, django-tailwind (latest), Node.js/npm (for Tailwind compilation)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
