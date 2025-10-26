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
        scandinavian_languages = ["da", "sv", "nb", "fi", "is"]
        for lang in scandinavian_languages:
            self.assertIn(
                lang,
                codes,
                f"Scandinavian language '{lang}' not in LANGUAGE_CHOICES",
            )


class LocaleSettingsSyncTests(TestCase, WagtailTestUtils):
    """
    Test automatic syncing between LocaleSettings and Locale model.

    CRITICAL: These tests ensure content is protected from accidental deletion.
    """

    def setUp(self):
        """Set up test data with locales and pages."""
        from wagtail.models import Locale, Page

        from home.models import HomePage

        # Get or create English locale
        self.locale_en, _ = Locale.objects.get_or_create(language_code="en")

        # Get root page
        self.root = Page.get_first_root_node()

        # Create English homepage with unique slug
        self.home_en = HomePage(
            title="Test Home",
            slug="test-home-sync",
            locale=self.locale_en,
        )
        self.root.add_child(instance=self.home_en)

        # Create site
        self.site = Site.objects.create(
            hostname="test-sync.localhost",
            root_page=self.home_en,
            is_default_site=False,
            site_name="Test Sync Site",
        )

    def test_locale_created_on_save(self):
        """Test that saving LocaleSettings creates new Locale records."""
        from wagtail.models import Locale

        # Initially only English exists
        self.assertEqual(Locale.objects.count(), 1)

        # Create settings with Finnish
        LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "fi"],
        )

        # Finnish locale should now exist
        self.assertTrue(Locale.objects.filter(language_code="fi").exists())
        self.assertEqual(Locale.objects.count(), 2)

    def test_multiple_locales_created_at_once(self):
        """Test creating multiple locales simultaneously."""
        from wagtail.models import Locale

        # Create settings with three languages
        LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "fi", "es", "fr"],
        )

        # All locales should exist
        self.assertTrue(Locale.objects.filter(language_code="en").exists())
        self.assertTrue(Locale.objects.filter(language_code="fi").exists())
        self.assertTrue(Locale.objects.filter(language_code="es").exists())
        self.assertTrue(Locale.objects.filter(language_code="fr").exists())
        self.assertEqual(Locale.objects.count(), 4)

    def test_cannot_remove_locale_with_pages(self):
        """
        CRITICAL TEST: Ensure content protection works.
        Test that removing a locale with pages raises validation error.
        """
        from wagtail.models import Locale

        from content.models import ContentPage
        from home.models import HomePage

        # Create Finnish locale and pages
        locale_fi, _ = Locale.objects.get_or_create(language_code="fi")

        home_fi = HomePage(
            title="Koti",
            slug="koti",
            locale=locale_fi,
            translation_key=self.home_en.translation_key,
        )
        self.root.add_child(instance=home_fi)

        # Create a Finnish content page
        finnish_page = ContentPage(
            title="Testi Sivu",
            slug="testi-sivu",
            locale=locale_fi,
        )
        home_fi.add_child(instance=finnish_page)

        # Create LocaleSettings with both languages
        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "fi"],
        )

        # Try to remove Finnish (should fail)
        settings.available_languages = ["en"]

        with self.assertRaises(ValidationError) as cm:
            settings.clean()

        # Check error message
        error_dict = cm.exception.message_dict
        self.assertIn("available_languages", error_dict)
        error_message = error_dict["available_languages"][0]

        # Should mention Finnish and page count
        self.assertIn("Finnish", error_message)
        self.assertIn("2", error_message)  # 2 pages: home + content page

    def test_error_message_includes_page_count(self):
        """Test that error message shows exact number of affected pages."""
        from wagtail.models import Locale

        from content.models import ContentPage
        from home.models import HomePage

        # Create Finnish locale
        locale_fi, _ = Locale.objects.get_or_create(language_code="fi")

        home_fi = HomePage(
            title="Koti",
            slug="koti",
            locale=locale_fi,
        )
        self.root.add_child(instance=home_fi)

        # Create multiple Finnish pages
        for i in range(5):
            page = ContentPage(
                title=f"Finnish Page {i}",
                slug=f"finnish-page-{i}",
                locale=locale_fi,
            )
            home_fi.add_child(instance=page)

        # Create settings
        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "fi"],
        )

        # Try to remove Finnish
        settings.available_languages = ["en"]

        with self.assertRaises(ValidationError) as cm:
            settings.clean()

        error_message = cm.exception.message_dict["available_languages"][0]
        # Should show 6 pages (1 home + 5 content pages)
        self.assertIn("6", error_message)

    def test_can_remove_locale_without_pages(self):
        """Test that removing a locale without pages is allowed."""
        from wagtail.models import Locale

        # Create Spanish locale without any pages
        Locale.objects.create(language_code="es")

        settings = LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "es"],
        )

        # Remove Spanish (should work because no pages)
        settings.available_languages = ["en"]
        settings.clean()  # Should not raise
        settings.save()

    def test_locales_not_automatically_deleted(self):
        """
        Test that Locale records aren't automatically deleted from database.
        They may still exist even if removed from LocaleSettings.
        """
        from wagtail.models import Locale

        LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "fi", "es"],
        )

        # All locales should exist
        self.assertTrue(Locale.objects.filter(language_code="fi").exists())
        self.assertTrue(Locale.objects.filter(language_code="es").exists())

        # Remove Finnish and Spanish from settings (no pages exist, so it's valid)
        settings = LocaleSettings.objects.get(site=self.site)
        settings.available_languages = ["en"]
        settings.save()

        # Locales should still exist in database
        self.assertTrue(Locale.objects.filter(language_code="fi").exists())
        self.assertTrue(Locale.objects.filter(language_code="es").exists())

    def test_validation_on_update_not_create(self):
        """Test that content validation only happens on update, not initial creation."""
        from wagtail.models import Locale

        from home.models import HomePage

        # Create Finnish locale with pages
        locale_fi, _ = Locale.objects.get_or_create(language_code="fi")
        home_fi = HomePage(
            title="Koti",
            slug="koti",
            locale=locale_fi,
        )
        if self.root:
            self.root.add_child(instance=home_fi)

        # Creating NEW settings should work even if Finnish has pages
        # (because we're not "removing" it, we're just not including it initially)
        LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en"],
        )

        # Verify settings were created successfully
        settings = LocaleSettings.objects.get(site=self.site)
        self.assertEqual(settings.available_languages, ["en"])


class SyncLocalesCommandTests(TestCase):
    """Test the sync_locales management command."""

    def setUp(self):
        """Set up test data."""
        from wagtail.models import Locale, Page

        from home.models import HomePage

        # Create English locale
        self.locale_en, _ = Locale.objects.get_or_create(language_code="en")

        # Create pages
        self.root = Page.get_first_root_node()
        self.home = HomePage(
            title="Command Test Home",
            slug="command-test-home",
            locale=self.locale_en,
        )
        self.root.add_child(instance=self.home)

        # Create site
        self.site = Site.objects.create(
            hostname="command-test.localhost",
            root_page=self.home,
            is_default_site=False,
            site_name="Command Test Site",
        )

    def test_command_creates_missing_locales(self):
        """Test that the command creates missing locales."""
        from io import StringIO

        from django.core.management import call_command
        from wagtail.models import Locale

        # Create settings with multiple languages
        LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en", "fi", "es"],
        )

        # Delete Finnish locale to simulate missing locale
        Locale.objects.filter(language_code="fi").delete()

        # Run command
        out = StringIO()
        call_command("sync_locales", stdout=out)

        # Finnish should be recreated
        self.assertTrue(Locale.objects.filter(language_code="fi").exists())
        output = out.getvalue()
        self.assertIn("fi", output.lower())

    def test_command_with_no_settings(self):
        """Test command behaves gracefully when no LocaleSettings exist."""
        from io import StringIO

        from django.core.management import call_command

        # Ensure no LocaleSettings exist
        LocaleSettings.objects.all().delete()

        # Run command
        out = StringIO()
        call_command("sync_locales", stdout=out)

        # Should report no settings found
        output = out.getvalue()
        self.assertIn("No LocaleSettings", output)

    def test_command_reports_locales_with_content(self):
        """Test that command reports when locales have content and can't be removed."""
        from io import StringIO

        from django.core.management import call_command
        from wagtail.models import Locale

        from home.models import HomePage

        # Create Finnish locale with pages
        locale_fi, _ = Locale.objects.get_or_create(language_code="fi")
        home_fi = HomePage(
            title="Koti",
            slug="koti",
            locale=locale_fi,
        )
        if self.root:
            self.root.add_child(instance=home_fi)

        # Create settings with only English
        LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en"],
        )

        # Run command with --remove-unused
        out = StringIO()
        call_command("sync_locales", "--remove-unused", stdout=out)

        output = out.getvalue()

        # Should report that Finnish can't be removed
        self.assertIn("fi", output.lower())
        self.assertIn("cannot remove", output.lower())

        # Finnish should still exist
        self.assertTrue(Locale.objects.filter(language_code="fi").exists())

    def test_command_shows_model_breakdown_for_locales_with_content(self):
        """Test that command shows which models prevent locale removal."""
        from io import StringIO

        from django.core.management import call_command
        from wagtail.models import Locale

        from content.models import ContentPage
        from home.models import HomePage

        # Create Finnish locale with multiple page types
        locale_fi, _ = Locale.objects.get_or_create(language_code="fi")
        home_fi = HomePage(
            title="Koti",
            slug="koti-breakdown",
            locale=locale_fi,
        )
        if self.root:
            self.root.add_child(instance=home_fi)

        # Add ContentPage
        content_fi = ContentPage(
            title="Sisältö",
            slug="sisalto",
            locale=locale_fi,
        )
        home_fi.add_child(instance=content_fi)

        # Create settings with only English
        LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en"],
        )

        # Run command with --remove-unused
        out = StringIO()
        call_command("sync_locales", "--remove-unused", stdout=out)

        output = out.getvalue()

        # Should show model breakdown
        # Note: wagtailcore.Page is also counted because it has a locale FK
        # and both HomePage and ContentPage inherit from it
        self.assertIn("home.HomePage", output)
        self.assertIn("content.ContentPage", output)
        self.assertIn("wagtailcore.Page", output)
        # Should show counts for each model
        self.assertIn("1 object(s)", output)
        # Should show total (HomePage + ContentPage + 2 Page records)
        self.assertIn("4 related object(s)", output)

        # Finnish should still exist
        self.assertTrue(Locale.objects.filter(language_code="fi").exists())

        # Finnish should still exist
        self.assertTrue(Locale.objects.filter(language_code="fi").exists())

    def test_command_removes_unused_locales(self):
        """Test that command removes locales without content when --remove-unused is used."""
        from io import StringIO

        from django.core.management import call_command
        from wagtail.models import Locale

        # Create Spanish locale without any pages
        Locale.objects.create(language_code="es")

        # Create settings with only English
        LocaleSettings.objects.create(
            site=self.site,
            default_language="en",
            available_languages=["en"],
        )

        # Run command with --remove-unused
        out = StringIO()
        call_command("sync_locales", "--remove-unused", stdout=out)

        # Spanish should be removed
        self.assertFalse(Locale.objects.filter(language_code="es").exists())

        output = out.getvalue()
        self.assertIn("es", output.lower())
        self.assertIn("removed", output.lower())
