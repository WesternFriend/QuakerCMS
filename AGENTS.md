# QuakerCMS - AI Coding Agent Instructions

## Project Overview

QuakerCMS is a **Wagtail-based CMS** for Quaker communities built with Django 5.2+ and Python 3.12+. It uses **uv** for package management and emphasizes runtime-configurable internationalization.

## Critical Architecture Patterns

### 1. Centralized Constants Pattern

**ALL language/i18n constants MUST be defined in `src/core/constants.py`**, never in settings or models directly:

```python
# ✅ CORRECT - Import from core.constants
from core.constants import DEFAULT_LANGUAGE_CODE, LANGUAGE_CHOICES

# ❌ WRONG - Don't define in settings or access via settings
settings.DEFAULT_LANGUAGE_CODE  # This doesn't exist!
```

**Why**: Settings are loaded once at startup. Constants in `core/constants.py` are the single source of truth for language configuration, used by:

- `src/core/settings/base.py` - Django settings
- `src/locales/models.py` - Model field choices
- `src/locales/utils.py` - Runtime utilities

### 2. Runtime Language Configuration

Languages are **configured at runtime** via `LocaleSettings` model in Wagtail admin, NOT in code:

- `LocaleSettings.save()` auto-creates `Locale` records (no manual sync needed in normal flow)
- Validation prevents deleting locales with content (shows model breakdown)
- Use `python manage.py sync_locales --remove-unused` to clean up unused locales
- Settings require **server restart** to take effect (Django loads at startup)

### 3. StreamField Block Architecture

Custom blocks use **StructBlock with templates** for semantic control:

```python
# Example: HeadingBlock restricts to h2-h4 (h1 reserved for page title)
class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, help_text="The heading text")
    level = blocks.ChoiceBlock(
        choices=[("h2", "Heading 2"), ("h3", "Heading 3"), ("h4", "Heading 4")],
        default="h2",
    )
    class Meta:
        template = "content/blocks/heading_block.html"
```

**Security**: Use `EmbedBlock` (oEmbed) for embedded content, NEVER `RawHTMLBlock` (XSS risk).

**Navigation Menu Pattern**: See `src/navigation/blocks.py` for nested block structure that enforces 2-level maximum:
- `TopLevelMenuBlock` (StreamBlock) contains page_link, external_link, OR dropdown
- `DropdownMenuBlock` (StructBlock) contains title and items (MenuItemBlock)
- `MenuItemBlock` (StreamBlock) contains ONLY page_link and external_link (no nested dropdowns)

This structural approach prevents 3+ level nesting at the schema level.

### 4. Translation & Locale Management

- Translation UI comes from `wagtail.contrib.simple_translation` (already installed)
- Content is **per-locale**, not auto-translated
- Use `copy_for_translation()` to create locale variants
- Management commands:
  - `show_language_settings` - Display current config (DB + settings + constants)
  - `sync_locales` - Sync Locale model with LocaleSettings (rarely needed)

## Development Workflow

### Essential Commands

**IMPORTANT**: This project uses `uv` for package management. When running Python commands in terminals (especially from AI assistants or automated tools), the virtual environment may not be automatically activated. **Always prefix Python commands with `uv run`** to ensure the correct environment is used:

```bash
# ✅ CORRECT - Use uv run for all Python commands
uv run python manage.py test
uv run python manage.py migrate
uv run python manage.py runserver

# ❌ WRONG - May fail if virtual environment isn't activated
python manage.py test
```

#### Package Management (from project root)

```bash
uv sync                    # Install all deps (creates .venv/)
uv add package-name        # Add runtime dependency
uv add --dev package-name  # Add dev dependency
```

#### Django Commands (from src/ directory)

```bash
cd src
uv run python manage.py migrate
uv run python manage.py test                    # Run all tests
uv run python manage.py test navigation         # Run specific app tests
uv run python manage.py createsuperuser         # One-time setup
uv run python manage.py runserver               # Development server
```

#### Code Quality (from project root)

```bash
uv run pre-commit install              # One-time setup
uv run pre-commit run --all-files      # Manual run
uv run ruff check --fix .              # Lint with auto-fix
uv run ruff format .                   # Format code
```

### Test Structure Conventions

Use **descriptive test classes** grouped by feature:

- `ModelTests` - Model behavior and validation
- `StreamFieldTests` - StreamField block testing
- `TranslationTests` - Locale/i18n functionality
- `AdminTests` - Admin interface integration
- `IntegrationTests` - Cross-app functionality

**Example test pattern**:

```python
def test_heading_block_supports_multiple_levels(self):
    """Test that heading block supports h2, h3, and h4 levels."""
    content_page = ContentPage(
        # ... setup ...
        body=[
            {"type": "heading", "value": {"text": "Main", "level": "h2"}},
            {"type": "heading", "value": {"text": "Sub", "level": "h3"}},
        ],
    )
    # Verify levels
    self.assertEqual(content_page.body[0].value["level"], "h2")
```

## File Organization

### Project Structure

```text
src/
├── core/                   # Django settings + centralized constants
│   ├── constants.py       # ⭐ ALL i18n constants defined here
│   └── settings/
│       ├── base.py        # Imports from core.constants
│       ├── dev.py         # Development settings
│       └── production.py  # Production settings
├── locales/               # Runtime language configuration
│   ├── models.py          # LocaleSettings with auto-sync
│   ├── utils.py           # get_language_settings() helper
│   └── management/commands/
│       ├── show_language_settings.py
│       └── sync_locales.py
├── content/               # General content pages
│   ├── models.py          # ContentPage with HeadingBlock
│   └── templates/content/blocks/
│       └── heading_block.html
├── home/                  # Home page app
└── search/                # Search functionality
```

### App Architecture

- **core** - Settings, constants, shared config (no models)
- **locales** - Runtime i18n configuration via Wagtail settings
- **content** - Flexible ContentPage with StreamField body
- **home** - HomePage model (site root)

## Common Pitfalls

### ❌ Don't Do This

```python
# Don't access constants via settings
from django.conf import settings
settings.DEFAULT_LANGUAGE_CODE  # AttributeError!

# Don't use RawHTMLBlock
("embed", blocks.RawHTMLBlock())  # XSS vulnerability

# Don't name blocks generically
("paragraph", blocks.RichTextBlock())  # Misleading - supports rich text
```

### ✅ Do This Instead

```python
# Import constants directly
from core.constants import DEFAULT_LANGUAGE_CODE, DEFAULT_LANGUAGES

# Use EmbedBlock for safety
("embed", EmbedBlock())  # Safe oEmbed integration

# Name blocks accurately
("rich_text", blocks.RichTextBlock())  # Clear intent
```

## Code Quality Standards

### Pre-commit Hooks (automatically enforced)

- **ruff** - Linting + formatting (replaces black/flake8/isort)
- **pyupgrade** - Modern Python syntax (3.12+)
- **django-upgrade** - Django 5.2+ patterns
- **djhtml** - Template formatting
- **curlylint** - Template linting

### Migration Best Practices

1. Test migrations are auto-generated
2. based on model changes
3. Run `python manage.py makemigrations` after model changes
4. All StreamField changes require migrations (block structure changes)
5. Check migration files into version control

## Debugging Tips

### Language Settings Not Working?

1. Check `src/core/constants.py` has the language code
2. Verify `LocaleSettings` exists in admin (Settings → Locale Settings)
3. Run `python manage.py show_language_settings` to debug
4. **Restart server** after changing LocaleSettings (settings load at startup)

### Tests Failing After StreamField Changes?

Update test data to match new block structure:

```python
# Old CharBlock format
{"type": "heading", "value": "My Heading"}

# New StructBlock format
{"type": "heading", "value": {"text": "My Heading", "level": "h2"}}
```

### Pre-commit Failing?

```bash
# Run checks to see what failed
uv run pre-commit run --all-files

# Common fixes
uv run ruff format .              # Fix formatting
uv run ruff check --fix .         # Auto-fix linting
```

## Additional Resources

- [Wagtail Documentation](https://docs.wagtail.org/) - CMS framework
- [Django 5.2 Documentation](https://docs.djangoproject.com/en/5.2/) - Web framework
- [uv Documentation](https://docs.astral.sh/uv/) - Package manager
- `src/locales/README.md` - Detailed i18n architecture guide
