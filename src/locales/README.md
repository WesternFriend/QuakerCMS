# Locales App - Runtime Language Configuration

The `locales` app allows administrators to configure site languages at runtime through the Wagtail admin interface, rather than having to modify settings files.

## Features

- **Runtime Configuration**: Change default language and available languages without redeploying
- **Site-Specific Settings**: Each Wagtail site can have its own language configuration
- **Fallback Mechanism**: Safe defaults ensure the site works even without configuration
- **Wide Language Support**: Includes 19+ languages commonly used by Quaker communities worldwide

## How It Works

### Settings Flow

1. **Centralized Constants** are defined in `core/constants.py`:
   - `DEFAULT_LANGUAGE_CODE = "en-us"` - Fallback default language
   - `DEFAULT_LANGUAGES = [("en", "English")]` - Fallback language list
   - `LANGUAGE_CHOICES` - All available language options (19+ languages)

2. **Runtime Loading**: On startup, the system attempts to load settings from `LocaleSettings` model:
   - Queries the database for the default Wagtail site's locale settings
   - If found, uses those values for `LANGUAGE_CODE`, `LANGUAGES`, and `WAGTAIL_CONTENT_LANGUAGES`
   - If not found or database is unavailable (e.g., during migrations), falls back to defaults from `core.constants`

3. **Admin Configuration**: Administrators can set languages via:
   - Wagtail Admin → Settings → Locale Settings

### Available Languages

The following languages are available (language code → display name):

- English (en)
- Spanish / Español (es)
- French / Français (fr)
- German / Deutsch (de)
- Portuguese / Português (pt)
- Italian / Italiano (it)
- Dutch / Nederlands (nl)
- Danish / Dansk (da)
- Swedish / Svenska (sv)
- Norwegian / Norsk (no)
- Finnish / Suomi (fi)
- Icelandic / Íslenska (is)
- Russian / Русский (ru)
- Japanese / 日本語 (ja)
- Chinese Simplified / 简体中文 (zh-hans)
- Chinese Traditional / 繁體中文 (zh-hant)
- Korean / 한국어 (ko)
- Arabic / العربية (ar)
- Swahili / Kiswahili (sw)

## Usage

### Viewing Current Settings

Use the management command to see current language configuration:

```bash
python manage.py show_language_settings
```

This displays:
- Default fallback values
- Current Django/Wagtail settings
- Per-site configuration from database

### Configuring Languages in Admin

1. Log into Wagtail Admin
2. Go to **Settings** → **Locale Settings**
3. Configure:
   - **Default Language**: Select the primary language for the site from the dropdown
   - **Available Languages**: Check the boxes for all languages you want to support
4. Save changes
5. Restart the application to apply changes

**Note**: The available languages must include the default language. The admin interface uses checkboxes for easy selection and prevents errors from manually typing language codes.

### Accessing Settings in Code

#### In Python Views

```python
from locales.models import LocaleSettings

def my_view(request):
    # Get locale settings for current site
    locale_settings = LocaleSettings.for_request(request)

    if locale_settings:
        default_lang = locale_settings.default_language
        available_langs = locale_settings.get_available_languages_list()
```

#### In Templates

Settings are available via the context processor:

```django
{{ settings.locales.LocaleSettings.default_language }}
{{ settings.locales.LocaleSettings.available_languages }}
```

## Model Reference

### LocaleSettings

**Fields:**
- `default_language` (CharField): The default language code for the site (dropdown selection)
- `available_languages` (JSONField): Array of language codes available on the site (checkbox selection in admin)

**Methods:**
- `get_available_languages_list()`: Returns list of tuples `[(code, name), ...]` from the JSON array
- `clean()`: Validates that default language is included in available languages and at least one language is selected

**Properties:**
- Site-specific (inherits from `BaseSiteSetting`)
- Accessible via Wagtail admin Settings menu
- Uses globe icon in admin
- User-friendly checkbox interface for language selection

## Important Notes

1. **Restart Required**: Changes to locale settings require an application restart to take effect (as Django loads settings at startup)

2. **Validation**: The model ensures the default language is always included in available languages

3. **Safe Fallbacks**: The system gracefully handles:
   - Missing database tables (during initial setup)
   - No configured settings (uses defaults)
   - Database connection issues

4. **Wagtail Integration**: Works seamlessly with Wagtail's built-in i18n features and the `wagtail.locales` app

5. **Centralized Constants**: All language-related constants are maintained in `core/constants.py` to ensure consistency across:
   - Django settings (`settings/base.py`)
   - Model choices (`locales/models.py`)
   - Utility functions (`locales/utils.py`)
   - This prevents constants from going out of sync and makes them easier to maintain

## Architecture

### File Structure

```
core/
  constants.py          # Centralized language constants
  settings/
    base.py            # Imports constants and configures i18n

locales/
  models.py            # LocaleSettings model (imports LANGUAGE_CHOICES)
  utils.py             # Helper functions (imports DEFAULT_* constants)
  management/
    commands/
      show_language_settings.py  # Display current configuration
```

### Constant Definitions

All language-related constants are defined in `core/constants.py`:

- **DEFAULT_LANGUAGE_CODE**: Fallback language code when no settings configured
- **DEFAULT_LANGUAGES**: Fallback language list (single tuple)
- **LANGUAGE_CHOICES**: Complete list of all available languages for admin selection

This centralized approach ensures that:
- Settings and model choices always match
- Constants are defined in one place
- Adding new languages is simple (update `core/constants.py` only)

## Future Enhancements

Potential improvements for future versions:

- Signal-based settings reload (avoid restart requirement)
- Language-specific content fallback configuration
- RTL language support indicators
- Language priority ordering
- Automatic locale creation in Wagtail when languages are added
