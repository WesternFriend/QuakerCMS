"""
Core constants for QuakerCMS.

This module contains shared constants used across the application,
particularly for internationalization and localization.

All language-related constants are centralized here to ensure consistency
across settings, models, and utilities. This prevents constants from going
out of sync when changes are made.

Usage:
    from core.constants import DEFAULT_LANGUAGE_CODE, LANGUAGE_CHOICES
"""

# Default fallback values for language settings
# These are used when no LocaleSettings have been configured
DEFAULT_LANGUAGE_CODE = "en-us"
DEFAULT_LANGUAGES = [("en", "English")]

# Common language choices available across Quaker communities worldwide
# Format: (language_code, display_name)
#
# Used by:
# - LocaleSettings model for admin dropdown choices
# - Settings configuration for fallback values
# - Utility functions for language lookups
LANGUAGE_CHOICES = [
    ("en", "English"),
    ("es", "Spanish / Español"),
    ("fr", "French / Français"),
    ("de", "German / Deutsch"),
    ("pt", "Portuguese / Português"),
    ("it", "Italian / Italiano"),
    ("nl", "Dutch / Nederlands"),
    ("da", "Danish / Dansk"),
    ("sv", "Swedish / Svenska"),
    ("no", "Norwegian / Norsk"),
    ("fi", "Finnish / Suomi"),
    ("is", "Icelandic / Íslenska"),
    ("ru", "Russian / Русский"),
    ("ja", "Japanese / 日本語"),
    ("zh-hans", "Chinese Simplified / 简体中文"),
    ("zh-hant", "Chinese Traditional / 繁體中文"),
    ("ko", "Korean / 한국어"),
    ("ar", "Arabic / العربية"),
    ("sw", "Swahili / Kiswahili"),
]
