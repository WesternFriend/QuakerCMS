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

    def test_scaffold_navbar_content_no_site_error(self):
        """Scaffold command fails gracefully with no site."""
        from io import StringIO

        from django.core.management import CommandError, call_command

        # Delete the default site
        Site.objects.all().delete()

        with self.assertRaises(CommandError) as context:
            call_command("scaffold_navbar_content", stdout=StringIO())

        self.assertIn("No default site found", str(context.exception))
