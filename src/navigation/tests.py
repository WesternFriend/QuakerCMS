"""Tests for navigation menu system."""

from django.test import TestCase
from wagtail.models import Locale, Site
from wagtail.test.utils import WagtailTestUtils

from home.models import HomePage
from navigation.models import NavigationMenuSetting


class ModelTests(TestCase):
    """Tests for NavigationMenuSetting model."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.get(is_default_site=True)

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
        # Get the home page
        home = HomePage.objects.first()

        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    "type": "page_link",
                    "value": {
                        "page": home.id,
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


class StreamFieldTests(TestCase):
    """Tests for StreamField block structure and validation."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.get(is_default_site=True)
        self.home = HomePage.objects.first()

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


class IntegrationTests(WagtailTestUtils, TestCase):
    """Integration tests for end-to-end menu rendering."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.get(is_default_site=True)
        self.locale = Locale.get_default()
        self.home = HomePage.objects.first()

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
