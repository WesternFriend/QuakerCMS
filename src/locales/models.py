from django import forms
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from core.constants import LANGUAGE_CHOICES


class MultipleLanguageField(models.JSONField):
    """Custom JSONField that works with CheckboxSelectMultiple widget."""

    def formfield(self, **kwargs):
        """Return a MultipleChoiceField for use in forms."""
        return forms.MultipleChoiceField(
            choices=LANGUAGE_CHOICES,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            **kwargs,
        )

    def get_prep_value(self, value):
        """Convert form data to JSON for storage."""
        if value is None:
            return []
        # If it's already a list, use it directly
        if isinstance(value, list):
            return value
        # If it's a string (shouldn't happen, but just in case)
        if isinstance(value, str):
            return [value]
        return list(value)


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

    # Store selected languages as a JSON array of language codes
    # This provides a better admin UI with checkboxes
    available_languages = MultipleLanguageField(
        default=list,
        blank=True,
        help_text="Select the languages available on this site. Must include the default language.",
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
        if not self.available_languages:
            return []

        return [
            (code, dict(LANGUAGE_CHOICES).get(code, code))
            for code in self.available_languages
            if code
        ]

    def clean(self):
        """
        Validate that the default language is included in available languages.
        Also warn if removing locales that have existing content.
        """
        from django.core.exceptions import ValidationError
        from wagtail.models import Locale, Page

        if not self.available_languages:
            raise ValidationError(
                {
                    "available_languages": "Please select at least one language.",
                },
            )

        if self.default_language not in self.available_languages:
            raise ValidationError(
                {
                    "available_languages": "Available languages must include the default language.",
                },
            )

        # Check if any locales are being removed that have existing content
        if self.pk:  # Only check if this is an existing record
            current_languages = set(self.available_languages or [])

            # Get existing locales from database
            existing_locales = Locale.objects.all()

            for locale in existing_locales:
                if locale.language_code not in current_languages:
                    # Check if this locale has any pages
                    page_count = Page.objects.filter(locale=locale).count()

                    if page_count > 0:
                        raise ValidationError(
                            {
                                "available_languages": (
                                    f"Cannot remove '{dict(LANGUAGE_CHOICES).get(locale.language_code, locale.language_code)}' "
                                    f"because it has {page_count} page(s) associated with it. "
                                    f"Please delete or move these pages first, or the locale will remain in the database."
                                ),
                            },
                        )

    def save(self, *args, **kwargs):
        """
        Save the settings and sync the Locale model to match available languages.
        """
        from wagtail.models import Locale

        # Save the settings first
        super().save(*args, **kwargs)

        # Sync Locale model with available languages
        if self.available_languages:
            # Get current locale codes in the database
            existing_locale_codes = set(
                Locale.objects.values_list("language_code", flat=True),
            )

            # Get desired locale codes from settings
            desired_locale_codes = set(self.available_languages)

            # Create new locales that don't exist yet
            for language_code in desired_locale_codes:
                if language_code not in existing_locale_codes:
                    Locale.objects.create(language_code=language_code)

            # Note: We don't delete locales here even if they're unchecked,
            # because they may have content. The clean() method validates this.

    def __str__(self):
        return f"Locale Settings for {self.site}"
