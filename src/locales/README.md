# Locales App - Runtime Language Configuration

The `locales` app allows administrators to configure site languages at runtime through the Wagtail admin interface, rather than having to modify settings files.

## Features

- **Runtime Configuration**: Change default language and available languages without redeploying
- **Site-Specific Settings**: Each Wagtail site can have its own language configuration
- **Automatic Locale Syncing**: Wagtail's `Locale` model is automatically synced with your settings
- **Content Protection**: Prevents deletion of locales that have existing content
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

4. **Automatic Syncing**: When you save `LocaleSettings`:
   - New locales are automatically created in Wagtail's `Locale` model
   - Settings are dynamically updated for Django and Wagtail
   - Validation prevents removing languages with existing content

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

### Syncing Locales

Sync Wagtail's `Locale` model with your `LocaleSettings`:

```bash
python manage.py sync_locales
```

This will:
- Create any missing `Locale` records for configured languages
- Display which locales were created

To also remove unused locales (that have no content):

```bash
python manage.py sync_locales --remove-unused
```

### Configuring Languages in Admin

1. Log into Wagtail Admin
2. Go to **Settings** → **Locale Settings**
3. Configure:
   - **Default Language**: Select the primary language for the site from the dropdown
   - **Available Languages**: Check the boxes for all languages you want to support
4. Save changes - **locales will be created automatically!**
5. Restart the application to apply changes to Django settings

**Important**: The available languages must include the default language. The system will validate this and show an error if you try to remove a language that has existing pages.

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
- `clean()`: Validates that:
  - At least one language is selected
  - Default language is included in available languages
  - Languages with existing content cannot be removed (shows error with page count)
- `save()`: Automatically creates `Locale` records for newly added languages

**Properties:**
- Site-specific (inherits from `BaseSiteSetting`)
- Accessible via Wagtail admin Settings menu
- Uses globe icon in admin
- User-friendly checkbox interface for language selection

## Content Protection

The app includes safeguards to prevent data loss:

### Validation on Save

When you try to remove a language from available languages:

1. **System checks** if that locale has any existing pages
2. **If pages exist**, validation fails with a clear error message:
   ```
   Cannot remove 'Finnish' because it has 5 page(s) associated with it.
   Please delete or move these pages first, or the locale will remain in the database.
   ```
3. **If no pages exist**, the language can be safely removed

### What Gets Protected

- Pages in that locale
- (Future: Snippets and other translatable models)

### How to Remove a Language Safely

1. **Check for content**: Look at the page explorer filtered by that locale
2. **Delete or translate**: Remove pages or translate them to another locale
3. **Then remove**: Uncheck the language in Locale Settings
4. **Optional cleanup**: Run `python manage.py sync_locales --remove-unused` to remove the unused `Locale` record

## Translation Workflow

1. **Configure languages** in Locale Settings (Settings → Locale Settings)
2. **Locales are created automatically** when you save
3. **Restart the server** to pick up new language settings in Django
4. **Translation UI appears** automatically (via `wagtail.contrib.simple_translation`)
5. **Translate content** using the "Translate" button in the page editor

## Important Notes

1. **Restart Required**: Changes to locale settings require an application restart for Django settings to reload (this affects `LANGUAGE_CODE`, `LANGUAGES`, and `WAGTAIL_CONTENT_LANGUAGES`)

2. **Automatic Locale Creation**: When you save LocaleSettings, new `Locale` records are created automatically - no manual sync needed in most cases

3. **Content Protection**: The system prevents you from removing languages that have content, protecting against accidental data loss

4. **Safe Fallbacks**: The system gracefully handles:
   - Missing database tables (during initial setup)
   - No configured settings (uses defaults)
   - Database connection issues

5. **Wagtail Integration**: Works seamlessly with:
   - Wagtail's built-in i18n features
   - `wagtail.contrib.simple_translation` for translation UI
   - `wagtail.locales` app for locale management

6. **Centralized Constants**: All language-related constants are maintained in `core/constants.py` to ensure consistency across:
   - Django settings (`settings/base.py`)
   - Model choices (`locales/models.py`)
   - Utility functions (`locales/utils.py`)

## Architecture

### File Structure

```
core/
  constants.py          # Centralized language constants
  settings/
    base.py            # Imports constants and configures i18n

locales/
  models.py            # LocaleSettings model with auto-sync
  utils.py             # Helper functions for loading settings
  management/
    commands/
      show_language_settings.py  # Display current configuration
      sync_locales.py            # Manual locale syncing
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

## Troubleshooting

### Translation button not appearing?

1. Check you have **multiple locales** configured (at least 2)
2. Ensure `WAGTAIL_I18N_ENABLED = True` in settings
3. Verify `wagtail.contrib.simple_translation` is in `INSTALLED_APPS`
4. **Restart the development server** to pick up new settings
5. Check that `Locale` records exist: Go to Settings → Locales in admin

### Can't remove a language?

If you see a validation error when unchecking a language:
1. Check how many pages use that locale (shown in the error message)
2. Delete those pages or translate them to another locale
3. Then you can remove the language from settings

### Locales not syncing?

If locales aren't being created automatically:
1. Check for errors when saving LocaleSettings
2. Run the sync command manually: `python manage.py sync_locales`
3. Verify your `available_languages` field is being saved correctly

### Server needs restart after language changes?

This is expected behavior - Django loads settings at startup:
1. Make language changes in admin
2. Restart the development server
3. New languages will be available

## Future Enhancements

Potential improvements for future versions:

- Signal-based settings reload (avoid restart requirement)
- Language-specific content fallback configuration
- RTL language support indicators
- Language priority ordering
- Support for translatable snippets in validation
- Migration helpers for changing language codes
