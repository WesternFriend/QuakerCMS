"""
Utility functions for loading locale settings dynamically.
"""

from core.constants import DEFAULT_LANGUAGE_CODE, DEFAULT_LANGUAGES


def get_language_settings():
    """
    Get language settings from LocaleSettings model with fallback to defaults.

    Returns a tuple of (language_code, languages_list).
    """
    try:
        # Import here to avoid circular imports
        from wagtail.models import Site

        from locales.models import LocaleSettings

        # Get the default site
        site = Site.objects.filter(is_default_site=True).first()

        if not site:
            # No default site, try to get any site
            site = Site.objects.first()

        if site:
            # Try to get locale settings for this site
            locale_settings = LocaleSettings.objects.filter(site=site).first()

            if locale_settings:
                # Use settings from database
                language_code = locale_settings.default_language
                languages = locale_settings.get_available_languages_list()
                return language_code, languages

        # No site or settings found, use defaults
        return DEFAULT_LANGUAGE_CODE, DEFAULT_LANGUAGES

    except Exception:
        # Database not ready, tables don't exist, or other error
        # This happens during initial migrations or startup
        return DEFAULT_LANGUAGE_CODE, DEFAULT_LANGUAGES
