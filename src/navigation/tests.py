"""Tests for navigation menu system."""

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from wagtail.models import Locale, Site
from wagtail.test.utils import WagtailTestUtils

from content.models import ContentPage
from home.models import HomePage
from navigation.blocks import DropdownMenuBlock
from navigation.models import NavigationMenuSetting
from navigation.templatetags.navigation_tags import process_menu_item


class ModelTests(TestCase):
    """Tests for NavigationMenuSetting model."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.get(is_default_site=True)
        # Ensure a HomePage exists for tests
        self.home = HomePage.objects.first()
        if not self.home:
            # Get the root page
            root = Site.objects.get(is_default_site=True).root_page
            self.home = HomePage(
                title="Test Home Page",
                slug="home",
            )
            root.add_child(instance=self.home)
            self.home.save_revision().publish()

    def test_create_navigation_menu_setting(self):
        """Can create navigation menu setting."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[],
        )
        self.assertEqual(menu.site, self.site)
        self.assertEqual(len(menu.menu_items), 0)

    def test_navigation_menu_with_page_link(self):
        """Can create menu with page link."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "page_link",
                    "value": {
                        "page": self.home.id,
                        "custom_title": "",
                        "anchor": "",
                    },
                },
            ],
        )
        self.assertEqual(len(menu.menu_items), 1)
        self.assertEqual(menu.menu_items[0].block_type, "page_link")

    def test_navigation_menu_with_external_link(self):
        """Can create menu with external link."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "external_link",
                    "value": {
                        "url": "https://example.com",
                        "title": "Example",
                        "anchor": "",
                    },
                },
            ],
        )
        self.assertEqual(len(menu.menu_items), 1)
        self.assertEqual(menu.menu_items[0].block_type, "external_link")

    def test_navigation_menu_for_request(self):
        """Can retrieve navigation menu for a request."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[],
        )

        factory = RequestFactory()
        request = factory.get("/")
        request.site = self.site

        retrieved_menu = NavigationMenuSetting.for_request(request)
        self.assertEqual(retrieved_menu.id, menu.id)


class StreamFieldTests(TestCase):
    """Tests for StreamField block structure and validation."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.get(is_default_site=True)
        # Ensure a HomePage exists for tests
        self.home = HomePage.objects.first()
        if not self.home:
            # Get the root page
            root = Site.objects.get(is_default_site=True).root_page
            self.home = HomePage(
                title="Test Home Page",
                slug="home",
            )
            root.add_child(instance=self.home)
            self.home.save_revision().publish()

    def test_page_link_block_has_required_fields(self):
        """PageLinkBlock has page, custom_title, and anchor fields."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "page_link",
                    "value": {
                        "page": self.home.id,
                        "custom_title": "Home Page",
                        "anchor": "section",
                    },
                },
            ],
        )
        block = menu.menu_items[0]
        self.assertEqual(block.value["page"].id, self.home.id)
        self.assertEqual(block.value["custom_title"], "Home Page")
        self.assertEqual(block.value["anchor"], "section")

    def test_external_link_block_has_required_fields(self):
        """ExternalLinkBlock has url, title, and anchor fields."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "external_link",
                    "value": {
                        "url": "https://example.com/docs",
                        "title": "Documentation",
                        "anchor": "getting-started",
                    },
                },
            ],
        )
        block = menu.menu_items[0]
        self.assertEqual(block.value["url"], "https://example.com/docs")
        self.assertEqual(block.value["title"], "Documentation")
        self.assertEqual(block.value["anchor"], "getting-started")

    def test_dropdown_block_structure(self):
        """Dropdown menu block contains title and child items."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "dropdown",
                    "value": {
                        "title": "Resources",
                        "items": [
                            {
                                "type": "page_link",
                                "value": {
                                    "page": self.home.id,
                                    "custom_title": "User Guide",
                                    "anchor": "",
                                },
                            },
                        ],
                    },
                },
            ],
        )
        block = menu.menu_items[0]
        self.assertEqual(block.block_type, "dropdown")
        self.assertEqual(block.value["title"], "Resources")
        self.assertEqual(len(block.value["items"]), 1)
        self.assertEqual(block.value["items"][0].block_type, "page_link")

    def test_dropdown_block_validates_non_empty_items(self):
        """Dropdown menu block requires at least one item."""
        block = DropdownMenuBlock()

        # Empty items should raise validation error
        with self.assertRaises(ValidationError) as context:
            block.clean({"title": "Empty Dropdown", "items": []})

        self.assertIn(
            "Dropdown menu must contain at least one item",
            str(context.exception),
        )


class IntegrationTests(WagtailTestUtils, TestCase):
    """Integration tests for end-to-end menu rendering."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.get(is_default_site=True)
        self.locale = Locale.get_default()
        # Ensure a HomePage exists for tests
        self.home = HomePage.objects.first()
        if not self.home:
            # Get the root page
            root = Site.objects.get(is_default_site=True).root_page
            self.home = HomePage(
                title="Test Home Page",
                slug="home",
            )
            root.add_child(instance=self.home)
            self.home.save_revision().publish()

    def test_create_menu_with_multiple_items(self):
        """Can create menu with multiple page and external links."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "page_link",
                    "value": {
                        "page": self.home.id,
                        "custom_title": "",
                        "anchor": "",
                    },
                },
                {
                    "type": "external_link",
                    "value": {
                        "url": "https://example.com",
                        "title": "Example",
                        "anchor": "",
                    },
                },
            ],
        )

        self.assertEqual(len(menu.menu_items), 2)
        self.assertEqual(menu.menu_items[0].block_type, "page_link")
        self.assertEqual(menu.menu_items[1].block_type, "external_link")


class TemplateTagTests(WagtailTestUtils, TestCase):
    """Tests for navigation template tags."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.site = Site.objects.get(is_default_site=True)
        self.default_locale = Locale.get_default()
        self.home = HomePage.objects.first()

        # Create a content page for testing
        self.about_page = ContentPage(
            title="About",
            slug="about",
            locale=self.default_locale,
        )
        self.home.add_child(instance=self.about_page)
        self.about_page.save_revision().publish()

    def _create_mock_block(self, block_type, value):
        """Helper to create mock block values for testing."""

        class MockBlockValue:
            def __init__(self, bt, val):
                self.block_type = bt
                self.value = val

        return MockBlockValue(block_type, value)

    def test_process_menu_item_page_link(self):
        """Process page link returns correct structure."""
        value = {
            "page": self.home,
            "custom_title": "Custom Home",
            "anchor": "top",
        }

        item = self._create_mock_block("page_link", value)

        result = process_menu_item(
            item,
            self.default_locale,
            self.default_locale,
            self.home,
        )

        self.assertEqual(result["type"], "page_link")
        self.assertEqual(result["title"], "Custom Home")
        self.assertIn("#top", result["url"])
        self.assertTrue(result["is_current"])

    def test_process_menu_item_page_link_without_custom_title(self):
        """Process page link uses page title when custom title is empty."""
        value = {
            "page": self.home,
            "custom_title": "",
            "anchor": "",
        }

        item = self._create_mock_block("page_link", value)

        result = process_menu_item(
            item,
            self.default_locale,
            self.default_locale,
        )

        self.assertEqual(result["title"], self.home.title)
        self.assertFalse(result["is_current"])

    def test_process_menu_item_external_link(self):
        """Process external link returns correct structure."""
        value = {
            "url": "https://example.com",
            "title": "Example Site",
            "anchor": "section",
        }

        item = self._create_mock_block("external_link", value)

        result = process_menu_item(
            item,
            self.default_locale,
            self.default_locale,
        )

        self.assertEqual(result["type"], "external_link")
        self.assertEqual(result["url"], "https://example.com#section")
        self.assertEqual(result["title"], "Example Site")
        self.assertFalse(result["is_current"])

    def test_process_menu_item_external_link_without_anchor(self):
        """Process external link works without anchor."""
        value = {
            "url": "https://example.com",
            "title": "Example",
            "anchor": "",
        }

        item = self._create_mock_block("external_link", value)

        result = process_menu_item(
            item,
            self.default_locale,
            self.default_locale,
        )

        self.assertEqual(result["url"], "https://example.com")

    def test_process_menu_item_dropdown(self):
        """Process dropdown with children."""
        page_value = {
            "page": self.about_page,
            "custom_title": "",
            "anchor": "",
        }

        child_item = self._create_mock_block("page_link", page_value)

        dropdown_value = {
            "title": "Resources",
            "items": [child_item],
        }

        dropdown_item = self._create_mock_block("dropdown", dropdown_value)

        result = process_menu_item(
            dropdown_item,
            self.default_locale,
            self.default_locale,
        )

        self.assertEqual(result["type"], "dropdown")
        self.assertEqual(result["title"], "Resources")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["type"], "page_link")
        self.assertFalse(result["is_open"])

    def test_process_menu_item_dropdown_with_current_page(self):
        """Process dropdown marks is_open when contains current page."""
        page_value = {
            "page": self.about_page,
            "custom_title": "",
            "anchor": "",
        }

        child_item = self._create_mock_block("page_link", page_value)

        dropdown_value = {
            "title": "Resources",
            "items": [child_item],
        }

        dropdown_item = self._create_mock_block("dropdown", dropdown_value)

        result = process_menu_item(
            dropdown_item,
            self.default_locale,
            self.default_locale,
            self.about_page,  # Current page
        )

        self.assertTrue(result["is_open"])

    def test_process_menu_item_dropdown_empty_children(self):
        """Process dropdown returns None when all children are invalid."""
        dropdown_value = {
            "title": "Empty Dropdown",
            "items": [],
        }

        dropdown_item = self._create_mock_block("dropdown", dropdown_value)

        result = process_menu_item(
            dropdown_item,
            self.default_locale,
            self.default_locale,
        )

        self.assertIsNone(result)

    def test_process_menu_item_page_link_unpublished_page(self):
        """Process page link returns None for unpublished page."""
        # Create unpublished page
        unpublished_page = ContentPage(
            title="Draft",
            slug="draft",
            locale=self.default_locale,
            live=False,
        )
        self.home.add_child(instance=unpublished_page)

        value = {
            "page": unpublished_page,
            "custom_title": "",
            "anchor": "",
        }

        item = self._create_mock_block("page_link", value)

        result = process_menu_item(
            item,
            self.default_locale,
            self.default_locale,
        )

        self.assertIsNone(result)

    def test_process_menu_item_page_link_none_page(self):
        """Process page link returns None when page is None."""
        value = {
            "page": None,
            "custom_title": "",
            "anchor": "",
        }

        item = self._create_mock_block("page_link", value)

        result = process_menu_item(
            item,
            self.default_locale,
            self.default_locale,
        )

        self.assertIsNone(result)

    def test_process_menu_item_unknown_type(self):
        """Process menu item returns None for unknown type."""
        value = {}

        item = self._create_mock_block("unknown_type", value)

        result = process_menu_item(
            item,
            self.default_locale,
            self.default_locale,
        )

        self.assertIsNone(result)

    def test_navigation_menu_tag_with_empty_menu(self):
        """Navigation menu tag returns empty list when no menu items."""
        NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[],
        )

        request = self.factory.get("/")
        request.site = self.site

        from django.template import Context, Template

        template = Template("{% load navigation_tags %}{% navigation_menu %}")
        context = Context({"request": request, "page": self.home})

        # Should not raise error
        result = template.render(context)
        self.assertIsNotNone(result)

    def test_navigation_menu_tag_without_settings(self):
        """Navigation menu tag handles missing settings gracefully."""
        request = self.factory.get("/")
        request.site = self.site

        from django.template import Context, Template

        # Delete any existing settings
        NavigationMenuSetting.objects.filter(site=self.site).delete()

        template = Template("{% load navigation_tags %}{% navigation_menu %}")
        context = Context({"request": request, "page": self.home})

        # Should not raise error
        result = template.render(context)
        self.assertIsNotNone(result)

    def test_navigation_menu_tag_renders_page_links(self):
        """Navigation menu tag renders page links correctly."""
        NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "page_link",
                    "value": {
                        "page": self.home.id,
                        "custom_title": "Home",
                        "anchor": "",
                    },
                },
                {
                    "type": "page_link",
                    "value": {
                        "page": self.about_page.id,
                        "custom_title": "",
                        "anchor": "section",
                    },
                },
            ],
        )

        request = self.factory.get("/")
        request.site = self.site

        from django.template import Context, Template

        template = Template("{% load navigation_tags %}{% navigation_menu %}")
        context = Context({"request": request, "page": self.home})

        result = template.render(context)
        self.assertIn("Home", result)
        self.assertIn("About", result)

    def test_navigation_menu_tag_renders_external_links(self):
        """Navigation menu tag renders external links correctly."""
        NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "external_link",
                    "value": {
                        "url": "https://example.com",
                        "title": "Example Site",
                        "anchor": "",
                    },
                },
            ],
        )

        request = self.factory.get("/")
        request.site = self.site

        from django.template import Context, Template

        template = Template("{% load navigation_tags %}{% navigation_menu %}")
        context = Context({"request": request, "page": self.home})

        result = template.render(context)
        self.assertIn("Example Site", result)
        self.assertIn("https://example.com", result)

    def test_navigation_menu_tag_renders_dropdowns(self):
        """Navigation menu tag renders dropdown menus correctly."""
        NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "dropdown",
                    "value": {
                        "title": "Resources",
                        "items": [
                            {
                                "type": "page_link",
                                "value": {
                                    "page": self.about_page.id,
                                    "custom_title": "About Us",
                                    "anchor": "",
                                },
                            },
                            {
                                "type": "external_link",
                                "value": {
                                    "url": "https://docs.example.com",
                                    "title": "Documentation",
                                    "anchor": "",
                                },
                            },
                        ],
                    },
                },
            ],
        )

        request = self.factory.get("/")
        request.site = self.site

        from django.template import Context, Template

        template = Template("{% load navigation_tags %}{% navigation_menu %}")
        context = Context({"request": request, "page": self.home})

        result = template.render(context)
        self.assertIn("Resources", result)
        self.assertIn("About Us", result)
        self.assertIn("Documentation", result)

    def test_navigation_menu_tag_marks_current_page(self):
        """Navigation menu tag marks current page correctly."""
        NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "page_link",
                    "value": {
                        "page": self.home.id,
                        "custom_title": "Home",
                        "anchor": "",
                    },
                },
                {
                    "type": "page_link",
                    "value": {
                        "page": self.about_page.id,
                        "custom_title": "About",
                        "anchor": "",
                    },
                },
            ],
        )

        request = self.factory.get("/about/")
        request.site = self.site

        from django.template import Context, Template

        template = Template("{% load navigation_tags %}{% navigation_menu %}")
        context = Context({"request": request, "page": self.about_page})

        result = template.render(context)
        self.assertIn('aria-current="page"', result)

    def test_navigation_menu_tag_filters_unpublished_pages(self):
        """Navigation menu tag filters out unpublished pages."""
        # Create unpublished page
        draft_page = ContentPage(
            title="Draft",
            slug="draft",
            locale=self.default_locale,
            live=False,
        )
        self.home.add_child(instance=draft_page)

        NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "page_link",
                    "value": {
                        "page": draft_page.id,
                        "custom_title": "Draft",
                        "anchor": "",
                    },
                },
                {
                    "type": "page_link",
                    "value": {
                        "page": self.about_page.id,
                        "custom_title": "About",
                        "anchor": "",
                    },
                },
            ],
        )

        request = self.factory.get("/")
        request.site = self.site

        from django.template import Context, Template

        template = Template("{% load navigation_tags %}{% navigation_menu %}")
        context = Context({"request": request, "page": self.home})

        result = template.render(context)
        # Draft should not appear
        self.assertNotIn("Draft", result)
        # Published page should appear
        self.assertIn("About", result)


class TranslationTests(WagtailTestUtils, TestCase):
    """Tests for navigation menu translation and multi-lingual support."""

    def setUp(self):
        """Set up test data with multiple locales."""
        self.site = Site.objects.get(is_default_site=True)
        self.locale_en = Locale.get_default()
        self.locale_es, _ = Locale.objects.get_or_create(language_code="es")
        self.locale_fr, _ = Locale.objects.get_or_create(language_code="fr")

        # Get the English home page and create translations
        self.home_en = HomePage.objects.first()

        # Create Spanish home page translation
        self.home_es = self.home_en.copy_for_translation(self.locale_es)
        self.home_es.title = "Inicio"
        self.home_es.save_revision().publish()

        # Create French home page translation
        self.home_fr = self.home_en.copy_for_translation(self.locale_fr)
        self.home_fr.title = "Accueil"
        self.home_fr.save_revision().publish()

        # Create an English page
        self.page_en = ContentPage(
            title="About Us",
            slug="about-us",
            locale=self.locale_en,
            body=[
                {
                    "type": "rich_text",
                    "value": "<p>Welcome to our community.</p>",
                },
            ],
        )
        self.home_en.add_child(instance=self.page_en)
        self.page_en.save_revision().publish()

        # Create Spanish translation
        self.page_es = self.page_en.copy_for_translation(self.locale_es)
        self.page_es.title = "Sobre Nosotros"
        self.page_es.body = [
            {
                "type": "rich_text",
                "value": "<p>Bienvenido a nuestra comunidad.</p>",
            },
        ]
        self.page_es.save_revision().publish()

        # Create French translation
        self.page_fr = self.page_en.copy_for_translation(self.locale_fr)
        self.page_fr.title = "À Propos de Nous"
        self.page_fr.body = [
            {
                "type": "rich_text",
                "value": "<p>Bienvenue dans notre communauté.</p>",
            },
        ]
        self.page_fr.save_revision().publish()

        # Create navigation menu with the English page
        self.nav_settings = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "page_link",
                    "value": {
                        "page": self.page_en.id,
                        "custom_title": "",
                        "anchor": "",
                    },
                },
            ],
        )

    def test_menu_displays_translated_page_in_current_locale(self):
        """Menu items display pages in current locale."""
        # Test with Spanish locale
        with self.activate_locale(self.locale_es):
            item = self.nav_settings.menu_items[0]
            result = process_menu_item(
                item,
                self.locale_es,
                self.locale_en,
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["type"], "page_link")
            self.assertEqual(result["title"], "Sobre Nosotros")
            self.assertEqual(result["page"].id, self.page_es.id)
            self.assertEqual(result["page"].locale, self.locale_es)

    def test_menu_displays_translated_page_in_french_locale(self):
        """Menu items display pages in French locale."""
        # Test with French locale
        with self.activate_locale(self.locale_fr):
            item = self.nav_settings.menu_items[0]
            result = process_menu_item(
                item,
                self.locale_fr,
                self.locale_en,
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["type"], "page_link")
            self.assertEqual(result["title"], "À Propos de Nous")
            self.assertEqual(result["page"].id, self.page_fr.id)
            self.assertEqual(result["page"].locale, self.locale_fr)

    def test_menu_falls_back_to_default_locale(self):
        """Menu falls back to default locale when translation unavailable."""
        # Create a new locale without translation
        locale_de, _ = Locale.objects.get_or_create(language_code="de")

        # Try to get menu item in German (no translation exists)
        item = self.nav_settings.menu_items[0]
        result = process_menu_item(
            item,
            locale_de,
            self.locale_en,
        )

        # Should fall back to English
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "page_link")
        self.assertEqual(result["title"], "About Us")
        self.assertEqual(result["page"].id, self.page_en.id)
        self.assertEqual(result["page"].locale, self.locale_en)

    def test_dropdown_items_respect_locale(self):
        """Dropdown menu items are translated correctly."""
        # Create a parent page in English
        programs_en = ContentPage(
            title="Programs",
            slug="programs",
            locale=self.locale_en,
        )
        self.home_en.add_child(instance=programs_en)
        programs_en.save_revision().publish()

        # Create Spanish translation
        programs_es = programs_en.copy_for_translation(self.locale_es)
        programs_es.title = "Programas"
        programs_es.save_revision().publish()

        # Update navigation with dropdown
        self.nav_settings.menu_items = [
            {
                "type": "dropdown",
                "value": {
                    "title": "Resources",
                    "items": [
                        {
                            "type": "page_link",
                            "value": {
                                "page": self.page_en.id,
                                "custom_title": "",
                                "anchor": "",
                            },
                        },
                        {
                            "type": "page_link",
                            "value": {
                                "page": programs_en.id,
                                "custom_title": "",
                                "anchor": "",
                            },
                        },
                    ],
                },
            },
        ]
        self.nav_settings.save()

        # Test with Spanish locale
        item = self.nav_settings.menu_items[0]
        result = process_menu_item(
            item,
            self.locale_es,
            self.locale_en,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "dropdown")
        self.assertEqual(len(result["items"]), 2)

        # Check first child is Spanish translation
        self.assertEqual(result["items"][0]["title"], "Sobre Nosotros")
        self.assertEqual(result["items"][0]["page"].locale, self.locale_es)

        # Check second child is Spanish translation
        self.assertEqual(result["items"][1]["title"], "Programas")
        self.assertEqual(result["items"][1]["page"].locale, self.locale_es)

    def test_unpublished_translation_not_shown(self):
        """Unpublished translations are not shown in menu."""
        # Create a draft Spanish page (unpublished)
        draft_page_en = ContentPage(
            title="Draft Page",
            slug="draft-page",
            locale=self.locale_en,
        )
        self.home_en.add_child(instance=draft_page_en)
        draft_page_en.save_revision().publish()

        # Create Spanish translation but don't publish it
        draft_page_es = draft_page_en.copy_for_translation(self.locale_es)
        draft_page_es.title = "Página de Borrador"
        draft_page_es.live = False
        draft_page_es.save_revision()  # Save but don't publish

        # Update navigation with this page
        self.nav_settings.menu_items = [
            {
                "type": "page_link",
                "value": {
                    "page": draft_page_en.id,
                    "custom_title": "",
                    "anchor": "",
                },
            },
        ]
        self.nav_settings.save()

        # Try to get menu item in Spanish
        item = self.nav_settings.menu_items[0]
        result = process_menu_item(
            item,
            self.locale_es,
            self.locale_en,
        )

        # Should return None since the Spanish translation exists but is unpublished
        # This prevents showing stale content in the wrong language
        self.assertIsNone(result)

    def test_custom_title_used_regardless_of_locale(self):
        """Custom title is used instead of translated page title."""
        # Update navigation with custom title
        self.nav_settings.menu_items = [
            {
                "type": "page_link",
                "value": {
                    "page": self.page_en.id,
                    "custom_title": "Custom Title",
                    "anchor": "",
                },
            },
        ]
        self.nav_settings.save()

        # Test with Spanish locale
        item = self.nav_settings.menu_items[0]
        result = process_menu_item(
            item,
            self.locale_es,
            self.locale_en,
        )

        # Should use custom title, not translated title
        self.assertEqual(result["title"], "Custom Title")
        # But page should still be Spanish
        self.assertEqual(result["page"].locale, self.locale_es)

    def test_navigation_menu_tag_respects_active_locale(self):
        """Navigation menu template tag uses active locale."""
        from django.template import Context, Template

        factory = RequestFactory()
        request = factory.get("/")
        request.site = self.site

        # Activate Spanish locale
        with self.activate_locale(self.locale_es):
            template = Template("{% load navigation_tags %}{% navigation_menu %}")
            context = Context({"request": request, "page": self.home_en})

            result = template.render(context)

            # Should show Spanish title
            self.assertIn("Sobre Nosotros", result)
            self.assertNotIn("About Us", result)

    def test_mixed_locale_dropdown_with_fallback(self):
        """Dropdown handles mix of available and unavailable translations."""
        # Create another English page without Spanish translation
        no_translation_page = ContentPage(
            title="English Only",
            slug="english-only",
            locale=self.locale_en,
        )
        self.home_en.add_child(instance=no_translation_page)
        no_translation_page.save_revision().publish()

        # Create dropdown with both pages
        self.nav_settings.menu_items = [
            {
                "type": "dropdown",
                "value": {
                    "title": "Mixed",
                    "items": [
                        {
                            "type": "page_link",
                            "value": {
                                "page": self.page_en.id,
                                "custom_title": "",
                                "anchor": "",
                            },
                        },
                        {
                            "type": "page_link",
                            "value": {
                                "page": no_translation_page.id,
                                "custom_title": "",
                                "anchor": "",
                            },
                        },
                    ],
                },
            },
        ]
        self.nav_settings.save()

        # Test with Spanish locale
        item = self.nav_settings.menu_items[0]
        result = process_menu_item(
            item,
            self.locale_es,
            self.locale_en,
        )

        self.assertEqual(len(result["items"]), 2)
        # First item should be Spanish
        self.assertEqual(result["items"][0]["title"], "Sobre Nosotros")
        self.assertEqual(result["items"][0]["page"].locale, self.locale_es)
        # Second item should fall back to English
        self.assertEqual(result["items"][1]["title"], "English Only")
        self.assertEqual(result["items"][1]["page"].locale, self.locale_en)

    def activate_locale(self, locale):
        """Context manager to activate a specific locale."""
        from unittest.mock import patch

        return patch("wagtail.models.Locale.get_active", return_value=locale)


class ManagementCommandTests(WagtailTestUtils, TestCase):
    """Tests for navigation management commands."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.get(is_default_site=True)
        self.locale = Locale.get_default()
        self.home = HomePage.objects.first()

    def test_scaffold_navbar_content_creates_pages(self):
        """Scaffold command creates sample pages."""
        from io import StringIO

        from django.core.management import call_command

        out = StringIO()
        call_command("scaffold_navbar_content", "--skip-menu", stdout=out)

        # Check that pages were created
        self.assertTrue(ContentPage.objects.filter(title="About").exists())
        self.assertTrue(ContentPage.objects.filter(title="Programs").exists())
        self.assertTrue(ContentPage.objects.filter(title="Contact").exists())
        self.assertTrue(ContentPage.objects.filter(title="Adult Education").exists())
        self.assertTrue(ContentPage.objects.filter(title="Youth Programs").exists())

        output = out.getvalue()
        self.assertIn("Successfully scaffolded", output)

    def test_scaffold_navbar_content_creates_navigation_menu(self):
        """Scaffold command creates navigation menu."""
        from io import StringIO

        from django.core.management import call_command

        out = StringIO()
        call_command("scaffold_navbar_content", stdout=out)

        # Check navigation menu was created
        nav_settings = NavigationMenuSetting.for_site(self.site)
        self.assertIsNotNone(nav_settings)
        self.assertGreater(len(nav_settings.menu_items), 0)

        # Check for specific menu items
        menu_types = [item.block_type for item in nav_settings.menu_items]
        self.assertIn("page_link", menu_types)
        self.assertIn("dropdown", menu_types)
        self.assertIn("external_link", menu_types)

    def test_scaffold_navbar_content_delete_option(self):
        """Scaffold command with --delete removes existing content."""
        from io import StringIO

        from django.core.management import call_command

        # Create initial content
        call_command("scaffold_navbar_content", stdout=StringIO())

        # Verify content exists
        about_page = ContentPage.objects.filter(title="About").first()
        self.assertIsNotNone(about_page)
        initial_id = about_page.id

        # Run with --delete
        out = StringIO()
        call_command("scaffold_navbar_content", "--delete", stdout=out)

        # Verify old content was deleted and new content created
        new_about_page = ContentPage.objects.filter(title="About").first()
        self.assertIsNotNone(new_about_page)
        self.assertNotEqual(initial_id, new_about_page.id)

        output = out.getvalue()
        self.assertIn("Deleted", output)

    def test_scaffold_navbar_content_delete_only_scaffolded_pages(self):
        """Scaffold command with --delete only removes scaffolded pages, not all pages."""
        from io import StringIO

        from django.core.management import call_command

        # Create a non-scaffolded page that should NOT be deleted
        user_page = ContentPage(
            title="User Created Page",
            slug="user-page",
            locale=self.locale,
            body=[
                {
                    "type": "rich_text",
                    "value": "<p>This is a user-created page.</p>",
                },
            ],
        )
        self.home.add_child(instance=user_page)
        user_page.save_revision().publish()
        user_page_id = user_page.id

        # Create scaffolded content
        call_command("scaffold_navbar_content", stdout=StringIO())

        # Verify both scaffolded and user pages exist
        self.assertTrue(ContentPage.objects.filter(title="About").exists())
        self.assertTrue(ContentPage.objects.filter(title="User Created Page").exists())

        # Run with --delete
        out = StringIO()
        call_command("scaffold_navbar_content", "--delete", stdout=out)

        # Verify user page still exists (not deleted)
        user_page_after = ContentPage.objects.filter(id=user_page_id).first()
        self.assertIsNotNone(
            user_page_after,
            "User-created page should NOT be deleted by scaffold command",
        )
        self.assertEqual(user_page_after.title, "User Created Page")

        # Verify scaffolded pages were recreated (different IDs)
        new_about_page = ContentPage.objects.filter(title="About").first()
        self.assertIsNotNone(new_about_page)

        output = out.getvalue()
        self.assertIn("Deleted", output)

    def test_scaffold_navbar_content_delete_removes_descendants(self):
        """Scaffold command with --delete removes scaffolded pages and their descendants."""
        from io import StringIO

        from django.core.management import call_command

        # Create scaffolded content
        call_command("scaffold_navbar_content", stdout=StringIO())

        # Verify Programs page and its children exist
        programs_page = ContentPage.objects.filter(title="Programs").first()
        self.assertIsNotNone(programs_page)
        self.assertTrue(ContentPage.objects.filter(title="Adult Education").exists())
        self.assertTrue(ContentPage.objects.filter(title="Youth Programs").exists())

        programs_page_id = programs_page.id
        adult_ed_page = ContentPage.objects.filter(title="Adult Education").first()
        adult_ed_id = adult_ed_page.id

        # Run with --delete
        out = StringIO()
        call_command("scaffold_navbar_content", "--delete", stdout=out)

        # Verify old Programs page and its descendants were deleted
        self.assertFalse(
            ContentPage.objects.filter(id=programs_page_id).exists(),
            "Old Programs page should be deleted",
        )
        self.assertFalse(
            ContentPage.objects.filter(id=adult_ed_id).exists(),
            "Descendants of Programs page should be deleted",
        )

        # Verify new Programs page and children were created
        new_programs_page = ContentPage.objects.filter(title="Programs").first()
        self.assertIsNotNone(new_programs_page)
        self.assertNotEqual(new_programs_page.id, programs_page_id)
        self.assertTrue(ContentPage.objects.filter(title="Adult Education").exists())
        self.assertTrue(ContentPage.objects.filter(title="Youth Programs").exists())

        output = out.getvalue()
        self.assertIn("Deleted", output)

    def test_scaffold_navbar_content_delete_with_no_existing_content(self):
        """Scaffold command with --delete works when no scaffolded pages exist."""
        from io import StringIO

        from django.core.management import call_command

        # Ensure no scaffolded pages exist
        ContentPage.objects.filter(
            slug__in=["dev_about", "dev_programs", "dev_contact"],
        ).delete()

        # Run with --delete (should not error)
        out = StringIO()
        call_command("scaffold_navbar_content", "--delete", stdout=out)

        # Verify pages were created
        self.assertTrue(ContentPage.objects.filter(title="About").exists())
        self.assertTrue(ContentPage.objects.filter(title="Programs").exists())
        self.assertTrue(ContentPage.objects.filter(title="Contact").exists())

        output = out.getvalue()
        # Should not say "Deleted" since nothing was deleted
        self.assertNotIn("Deleted", output)

    def test_scaffold_navbar_content_is_idempotent(self):
        """Scaffold command can be run multiple times without --delete (idempotent)."""
        from io import StringIO

        from django.core.management import call_command

        # Run scaffold command first time
        call_command("scaffold_navbar_content", stdout=StringIO())

        # Verify initial content exists
        about_page = ContentPage.objects.filter(slug="dev_about").first()
        programs_page = ContentPage.objects.filter(slug="dev_programs").first()
        contact_page = ContentPage.objects.filter(slug="dev_contact").first()
        adult_ed_page = ContentPage.objects.filter(slug="dev_adult-education").first()

        self.assertIsNotNone(about_page)
        self.assertIsNotNone(programs_page)
        self.assertIsNotNone(contact_page)
        self.assertIsNotNone(adult_ed_page)

        # Store IDs to verify they don't change
        about_id = about_page.id
        programs_id = programs_page.id
        contact_id = contact_page.id
        adult_ed_id = adult_ed_page.id

        # Run scaffold command second time WITHOUT --delete
        # This should reuse existing pages, not create duplicates or fail
        out = StringIO()
        call_command("scaffold_navbar_content", stdout=out)

        # Verify pages still exist with SAME IDs (reused, not recreated)
        about_page_after = ContentPage.objects.filter(slug="dev_about").first()
        programs_page_after = ContentPage.objects.filter(slug="dev_programs").first()
        contact_page_after = ContentPage.objects.filter(slug="dev_contact").first()
        adult_ed_page_after = ContentPage.objects.filter(
            slug="dev_adult-education",
        ).first()

        self.assertIsNotNone(about_page_after)
        self.assertIsNotNone(programs_page_after)
        self.assertIsNotNone(contact_page_after)
        self.assertIsNotNone(adult_ed_page_after)

        # Verify IDs are the same (pages were reused, not recreated)
        self.assertEqual(about_page_after.id, about_id)
        self.assertEqual(programs_page_after.id, programs_id)
        self.assertEqual(contact_page_after.id, contact_id)
        self.assertEqual(adult_ed_page_after.id, adult_ed_id)

        # Verify no duplicate pages were created
        self.assertEqual(ContentPage.objects.filter(slug="dev_about").count(), 1)
        self.assertEqual(ContentPage.objects.filter(slug="dev_programs").count(), 1)
        self.assertEqual(ContentPage.objects.filter(slug="dev_contact").count(), 1)
        self.assertEqual(
            ContentPage.objects.filter(slug="dev_adult-education").count(),
            1,
        )

        output = out.getvalue()
        # On second run, all pages should be reused (not created)
        self.assertIn("Created 0 pages, reused 5 pages", output)

    def test_scaffold_navbar_content_no_site_error(self):
        """Scaffold command fails gracefully with no site."""
        from io import StringIO

        from django.core.management import CommandError, call_command

        # Delete the default site
        Site.objects.all().delete()

        with self.assertRaises(CommandError) as context:
            call_command("scaffold_navbar_content", stdout=StringIO())

        self.assertIn("No default site found", str(context.exception))

    def test_scaffold_navbar_content_skips_existing_menu(self):
        """Scaffold command skips menu update when menu already exists (without --force-menu)."""
        from io import StringIO

        from django.core.management import call_command

        # First run - creates menu
        call_command("scaffold_navbar_content", stdout=StringIO())

        # Get nav settings
        nav_settings = NavigationMenuSetting.for_site(self.site)

        # Modify the menu to simulate manual changes
        nav_settings.menu_items = [
            {
                "type": "external_link",
                "value": {
                    "url": "https://example.com",
                    "title": "Custom Link",
                    "anchor": "",
                },
                "id": "custom-link",
            },
        ]
        nav_settings.save()

        # Second run - should skip menu update
        out = StringIO()
        call_command("scaffold_navbar_content", stdout=out)

        # Verify menu was NOT overwritten
        nav_settings.refresh_from_db()
        self.assertEqual(len(nav_settings.menu_items), 1)
        self.assertEqual(nav_settings.menu_items[0].block_type, "external_link")
        self.assertEqual(nav_settings.menu_items[0].value["title"], "Custom Link")

        # Check warning message
        output = out.getvalue()
        self.assertIn("Navigation menu already exists", output)
        self.assertIn("Use --force-menu to overwrite", output)

    def test_scaffold_navbar_content_force_menu_overwrites(self):
        """Scaffold command with --force-menu overwrites existing menu."""
        from io import StringIO

        from django.core.management import call_command

        # First run - creates menu
        call_command("scaffold_navbar_content", stdout=StringIO())

        # Get initial menu
        nav_settings = NavigationMenuSetting.for_site(self.site)

        # Modify the menu to simulate manual changes
        nav_settings.menu_items = [
            {
                "type": "external_link",
                "value": {
                    "url": "https://example.com",
                    "title": "Custom Link",
                    "anchor": "",
                },
                "id": "custom-link",
            },
        ]
        nav_settings.save()

        # Second run with --force-menu - should overwrite
        out = StringIO()
        call_command("scaffold_navbar_content", "--force-menu", stdout=out)

        # Verify menu WAS overwritten
        nav_settings.refresh_from_db()
        self.assertGreater(len(nav_settings.menu_items), 1)

        # Check for scaffold menu items
        menu_types = [item.block_type for item in nav_settings.menu_items]
        self.assertIn("page_link", menu_types)
        self.assertIn("dropdown", menu_types)

        # Check success message (no warning)
        output = out.getvalue()
        self.assertIn("Updated NavigationMenuSetting", output)
        self.assertNotIn("already exists", output)
