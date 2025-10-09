"""
Tests for the locales app.

This test suite ensures the reliability of language configuration,
which is critical for international Quaker communities.
"""

from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.models import Site
from wagtail.test.utils import WagtailTestUtils

from core.constants import DEFAULT_LANGUAGE_CODE, DEFAULT_LANGUAGES, LANGUAGE_CHOICES
from locales.models import LocaleSettings, MultipleLanguageField
from locales.utils import get_language_settings


class MultipleLanguageFieldTests(TestCase):
    """Test the custom MultipleLanguageField."""

    def setUp(self):
        self.field = MultipleLanguageField(default=list)

    def test_formfield_returns_multiple_choice_field(self):
        """Test that formfield returns a MultipleChoiceField."""
        form_field = self.field.formfield()
        self.assertEqual(form_field.__class__.__name__, "MultipleChoiceField")

    def test_formfield_has_checkbox_widget(self):
        """Test that the form field uses CheckboxSelectMultiple widget."""
        form_field = self.field.formfield()
        self.assertEqual(form_field.widget.__class__.__name__, "CheckboxSelectMultiple")

    def test_formfield_has_correct_choices(self):
        """Test that the form field has all language choices."""
        form_field = self.field.formfield()
        self.assertEqual(form_field.choices, LANGUAGE_CHOICES)

    def test_get_prep_value_with_list(self):
        """Test that list values are preserved."""
        test_data = ["en", "fi", "es"]
        result = self.field.get_prep_value(test_data)
        self.assertEqual(result, test_data)
        self.assertIsInstance(result, list)

    def test_get_prep_value_with_none(self):
        """Test that None returns an empty list."""
        result = self.field.get_prep_value(None)
        self.assertEqual(result, [])

    def test_get_prep_value_with_tuple(self):
        """Test that tuples are converted to lists."""
        test_data = ("en", "fi", "es")
        result = self.field.get_prep_value(test_data)
        self.assertEqual(result, ["en", "fi", "es"])
        self.assertIsInstance(result, list)


class LocaleSettingsModelTests(TestCase, WagtailTestUtils):
    """Test the LocaleSettings model."""

    def setUp(self):
        # Get or create the default site
        self.site = Site.objects.get(is_default_site=True)

    def test_create_locale_settings(self):
        """Test creating locale settings for a site."""
        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "es", "fr"],
        )
        self.assertEqual(settings.default_language, "en")
        self.assertEqual(settings.available_languages, ["en", "es", "fr"])

    def test_get_available_languages_list(self):
        """Test that get_available_languages_list returns correct tuples."""
        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "fi", "es"],
        )
        result = settings.get_available_languages_list()
        expected = [
            ("en", "English"),
            ("fi", "Finnish / Suomi"),
            ("es", "Spanish / Español"),
        ]
        self.assertEqual(result, expected)

    def test_get_available_languages_list_empty(self):
        """Test that empty available_languages returns empty list."""
        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=[],
        )
        result = settings.get_available_languages_list()
        self.assertEqual(result, [])

    def test_default_language_must_be_in_available(self):
        """Test validation: default language must be in available languages."""
        settings = LocaleSettings(
            site=self.site,
            default_language="en",
            available_languages=["es", "fr"],  # Missing 'en'
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean()
        self.assertIn("available_languages", cm.exception.message_dict)

    def test_at_least_one_language_required(self):
        """Test validation: at least one language must be selected."""
        settings = LocaleSettings(
            site=self.site,
            default_language="en",
            available_languages=[],
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean()
        self.assertIn("available_languages", cm.exception.message_dict)

    def test_valid_settings_pass_validation(self):
        """Test that valid settings pass validation."""
        settings = LocaleSettings(
            site=self.site,
            default_language="en",
            available_languages=["en", "es", "fr"],
        )
        # Should not raise any exception
        settings.clean()

    def test_str_representation(self):
        """Test the string representation of LocaleSettings."""
        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en"],
        )
        expected = f"Locale Settings for {self.site}"
        self.assertEqual(str(settings), expected)

    def test_supports_all_language_choices(self):
        """Test that all language choices can be used."""
        all_codes = [code for code, name in LANGUAGE_CHOICES]
        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=all_codes,
        )
        self.assertEqual(len(settings.available_languages), len(LANGUAGE_CHOICES))


class LocaleUtilsTests(TestCase):
    """Test the locale utility functions."""

    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)

    def test_get_language_settings_with_no_settings(self):
        """Test fallback to defaults when no settings exist."""
        language_code, languages = get_language_settings()
        self.assertEqual(language_code, DEFAULT_LANGUAGE_CODE)
        self.assertEqual(languages, DEFAULT_LANGUAGES)

    def test_get_language_settings_with_settings(self):
        """Test loading settings from database."""
        LocaleSettings.objects.create(
            site=self.site,
            default_language="fi",
            available_languages=["fi", "en", "sv"],
        )
        language_code, languages = get_language_settings()
        self.assertEqual(language_code, "fi")
        expected_languages = [
            ("fi", "Finnish / Suomi"),
            ("en", "English"),
            ("sv", "Swedish / Svenska"),
        ]
        self.assertEqual(languages, expected_languages)

    def test_get_language_settings_returns_tuple(self):
        """Test that the function returns a tuple of (code, languages_list)."""
        result = get_language_settings()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        # First element should be a string (language code)
        self.assertIsInstance(result[0], str)
        # Second element should be a list of tuples
        self.assertIsInstance(result[1], list)

    def test_fallback_when_database_error(self):
        """Test fallback when database raises an error."""
        with patch("wagtail.models.Site.objects") as mock_objects:
            mock_objects.filter.side_effect = Exception("Database error")

            language_code, languages = get_language_settings()

            self.assertEqual(language_code, DEFAULT_LANGUAGE_CODE)
            self.assertEqual(languages, DEFAULT_LANGUAGES)

    def test_fallback_when_site_exists_but_no_settings(self):
        """Test fallback when a site exists but has no LocaleSettings."""
        # Remove the default site flag to trigger the "any site" fallback
        self.site.is_default_site = False
        self.site.save()

        # Create a non-default site as well
        Site.objects.create(
            hostname="example.com",
            port=80,
            site_name="Example Site",
            root_page_id=1,
            is_default_site=False,
        )

        # Should use first available site when no default site
        language_code, languages = get_language_settings()

        # Should use defaults since site has no settings
        self.assertEqual(language_code, DEFAULT_LANGUAGE_CODE)
        self.assertEqual(languages, DEFAULT_LANGUAGES)


class LocaleSettingsAdminTests(TestCase):
    """
    Test LocaleSettings integration with Wagtail admin.

    Note: These tests verify the model behavior rather than full admin integration,
    as full admin testing requires staticfiles collection which is complex in test environments.
    """

    def setUp(self):
        """Set up test site and user."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )

        # Create a site for testing
        self.site = Site.objects.create(
            hostname="testserver",
            port=80,
            site_name="Test Site",
            root_page_id=1,
            is_default_site=True,
        )

    def test_locale_settings_can_be_created_for_site(self):
        """Test that locale settings can be created for a site."""
        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="es",
            available_languages=["en", "es", "fr"],
        )

        self.assertEqual(settings.site, self.site)
        self.assertEqual(settings.default_language, "es")
        self.assertEqual(set(settings.available_languages), {"en", "es", "fr"})

    def test_locale_settings_for_site_method(self):
        """Test the for_site() method returns settings for specific site."""
        # Create settings for the site
        LocaleSettings.objects.create(
            site=self.site,
            default_language="fr",
            available_languages=["fr", "de"],
        )

        # Retrieve using for_site()
        settings = LocaleSettings.for_site(self.site)

        self.assertEqual(settings.default_language, "fr")
        self.assertEqual(set(settings.available_languages), {"fr", "de"})


class LanguageChoicesIntegrityTests(TestCase):
    """Test integrity of language choices constants."""

    def test_all_language_choices_are_valid_tuples(self):
        """Test that all language choices are valid (code, name) tuples."""
        for choice in LANGUAGE_CHOICES:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)
            code, name = choice
            self.assertIsInstance(code, str)
            self.assertIsInstance(name, str)
            self.assertTrue(len(code) >= 2)  # Language codes are at least 2 chars
            self.assertTrue(len(name) > 0)

    def test_language_codes_are_unique(self):
        """Test that all language codes are unique."""
        codes = [code for code, name in LANGUAGE_CHOICES]
        self.assertEqual(len(codes), len(set(codes)))

    def test_default_language_in_choices(self):
        """Test that the default fallback language is in choices."""
        codes = [code for code, name in LANGUAGE_CHOICES]
        # Extract just the language code without country (e.g., 'en' from 'en-us')
        default_base = DEFAULT_LANGUAGE_CODE.split("-")[0]
        # Check if either the full code or base code is in choices
        self.assertTrue(
            DEFAULT_LANGUAGE_CODE in codes or default_base in codes,
            f"Default language '{DEFAULT_LANGUAGE_CODE}' (or base '{default_base}') not in LANGUAGE_CHOICES",
        )

    def test_critical_languages_present(self):
        """Test that critical languages for Quaker communities are present."""
        codes = [code for code, name in LANGUAGE_CHOICES]
        critical_languages = ["en", "es", "fr"]  # English, Spanish, French
        for lang in critical_languages:
            self.assertIn(
                lang,
                codes,
                f"Critical language '{lang}' not in LANGUAGE_CHOICES",
            )

    def test_scandinavian_languages_present(self):
        """Test that Scandinavian languages are present."""
        codes = [code for code, name in LANGUAGE_CHOICES]
        scandinavian_languages = ["da", "sv", "no", "fi", "is"]
        for lang in scandinavian_languages:
            self.assertIn(
                lang,
                codes,
                f"Scandinavian language '{lang}' not in LANGUAGE_CHOICES",
            )
