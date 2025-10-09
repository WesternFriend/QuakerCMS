from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

# Common language choices that can be used across Quaker communities
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


@register_setting(icon="globe")
class LocaleSettings(BaseSiteSetting):
    """
    Site-specific locale settings allowing runtime configuration of available languages.
    """

    default_language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="en",
        help_text="The default language for this site",
    )

    # Using a simple text field to store multiple language codes (comma-separated)
    # This approach works well for the expected number of languages
    available_languages = models.TextField(
        default="en",
        help_text="Comma-separated list of language codes (e.g., 'en,es,fr'). Must include the default language.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("default_language"),
                FieldPanel("available_languages"),
            ],
            heading="Language Configuration",
        ),
    ]

    class Meta:
        verbose_name = "Locale Settings"

    def get_available_languages_list(self):
        """
        Returns a list of tuples (code, name) for available languages.
        """
        codes = [code.strip() for code in self.available_languages.split(",")]
        return [
            (code, dict(LANGUAGE_CHOICES).get(code, code)) for code in codes if code
        ]

    def clean(self):
        """
        Validate that the default language is included in available languages.
        """
        from django.core.exceptions import ValidationError

        available = [code.strip() for code in self.available_languages.split(",")]
        if self.default_language not in available:
            raise ValidationError(
                {
                    "available_languages": "Available languages must include the default language.",
                },
            )

    def __str__(self):
        return f"Locale Settings for {self.site}"
