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
        """
        from django.core.exceptions import ValidationError

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

    def __str__(self):
        return f"Locale Settings for {self.site}"
