"""
Tests for the content app.

This module tests the ContentPage model including:
- Page creation and hierarchy
- StreamField functionality
- Translation support
- Template rendering
- Parent/child page constraints
"""

from django.test import TestCase
from wagtail.models import Locale, Page, Site
from wagtail.test.utils import WagtailPageTestCase

from content.models import ContentPage
from home.models import HomePage


class ContentPageModelTests(WagtailPageTestCase):
    """Test ContentPage model constraints and behavior."""

    def setUp(self):
        """Set up test data."""
        # Get or create English locale
        self.locale_en, _ = Locale.objects.get_or_create(language_code="en")

        # Get root page
        self.root = Page.get_first_root_node()

        # Create HomePage
        self.home = HomePage(
            title="Test Home",
            slug="test-home-content",
            locale=self.locale_en,
        )
        self.root.add_child(instance=self.home)

        # Create site
        self.site = Site.objects.create(
            hostname="content-test.localhost",
            root_page=self.home,
            is_default_site=False,
            site_name="Content Test Site",
        )

    def test_can_create_content_page_under_homepage(self):
        """Test that ContentPage can be created as child of HomePage."""
        content_page = ContentPage(
            title="Test Content",
            slug="test-content",
            locale=self.locale_en,
        )
        self.home.add_child(instance=content_page)

        # Verify page was created
        self.assertTrue(ContentPage.objects.filter(slug="test-content").exists())
        self.assertEqual(content_page.get_parent(), self.home)

    def test_can_create_nested_content_pages(self):
        """Test that ContentPage can have ContentPage children."""
        parent_page = ContentPage(
            title="Parent Content",
            slug="parent-content",
            locale=self.locale_en,
        )
        self.home.add_child(instance=parent_page)

        child_page = ContentPage(
            title="Child Content",
            slug="child-content",
            locale=self.locale_en,
        )
        parent_page.add_child(instance=child_page)

        # Verify hierarchy
        self.assertEqual(child_page.get_parent(), parent_page)
        self.assertEqual(parent_page.get_children().count(), 1)
        # get_children() returns Page objects, need to get specific type
        self.assertEqual(parent_page.get_children().first().specific, child_page)

    def test_content_page_allowed_subpage_types(self):
        """Test that ContentPage only allows ContentPage as children."""
        self.assertEqual(ContentPage.subpage_types, ["content.ContentPage"])

    def test_content_page_allowed_parent_types(self):
        """Test that ContentPage can only be child of HomePage or ContentPage."""
        self.assertEqual(
            ContentPage.parent_page_types,
            ["home.HomePage", "content.ContentPage"],
        )

    def test_content_page_verbose_names(self):
        """Test verbose name and plural form."""
        self.assertEqual(ContentPage._meta.verbose_name, "Content Page")
        self.assertEqual(ContentPage._meta.verbose_name_plural, "Content Pages")

    def test_content_page_inherits_from_page(self):
        """Test that ContentPage inherits from Wagtail Page."""
        self.assertTrue(issubclass(ContentPage, Page))

    def test_body_field_is_optional(self):
        """Test that body StreamField can be blank."""
        content_page = ContentPage(
            title="Empty Content",
            slug="empty-content",
            locale=self.locale_en,
        )
        self.home.add_child(instance=content_page)

        # Should not raise validation error
        content_page.full_clean()
        # Empty StreamField should have zero blocks
        self.assertEqual(len(content_page.body), 0)

    def test_content_page_str_representation(self):
        """Test string representation uses title."""
        content_page = ContentPage(
            title="My Test Page",
            slug="my-test-page",
            locale=self.locale_en,
        )
        self.home.add_child(instance=content_page)

        self.assertEqual(str(content_page), "My Test Page")


class ContentPageStreamFieldTests(WagtailPageTestCase):
    """Test StreamField functionality in ContentPage."""

    def setUp(self):
        """Set up test data."""
        self.locale_en, _ = Locale.objects.get_or_create(language_code="en")
        self.root = Page.get_first_root_node()
        self.home = HomePage(
            title="Stream Test Home",
            slug="stream-test-home",
            locale=self.locale_en,
        )
        self.root.add_child(instance=self.home)

    def test_can_add_heading_block(self):
        """Test adding a heading block to body."""
        content_page = ContentPage(
            title="Heading Test",
            slug="heading-test",
            locale=self.locale_en,
            body=[
                {"type": "heading", "value": "My Heading"},
            ],
        )
        self.home.add_child(instance=content_page)

        # Verify heading block
        self.assertEqual(len(content_page.body), 1)
        self.assertEqual(content_page.body[0].block_type, "heading")
        self.assertEqual(content_page.body[0].value, "My Heading")

    def test_can_add_paragraph_block(self):
        """Test adding a paragraph block to body."""
        content_page = ContentPage(
            title="Paragraph Test",
            slug="paragraph-test",
            locale=self.locale_en,
            body=[
                {"type": "paragraph", "value": "<p>My paragraph text</p>"},
            ],
        )
        self.home.add_child(instance=content_page)

        # Verify paragraph block
        self.assertEqual(len(content_page.body), 1)
        self.assertEqual(content_page.body[0].block_type, "paragraph")

    def test_can_add_quote_block(self):
        """Test adding a quote block to body."""
        content_page = ContentPage(
            title="Quote Test",
            slug="quote-test",
            locale=self.locale_en,
            body=[
                {"type": "quote", "value": "Inspirational quote here"},
            ],
        )
        self.home.add_child(instance=content_page)

        # Verify quote block
        self.assertEqual(len(content_page.body), 1)
        self.assertEqual(content_page.body[0].block_type, "quote")

    def test_can_add_embed_block(self):
        """Test adding an embed block to body."""
        content_page = ContentPage(
            title="Embed Test",
            slug="embed-test",
            locale=self.locale_en,
            body=[
                {"type": "embed", "value": "<iframe>Embedded content</iframe>"},
            ],
        )
        self.home.add_child(instance=content_page)

        # Verify embed block
        self.assertEqual(len(content_page.body), 1)
        self.assertEqual(content_page.body[0].block_type, "embed")

    def test_can_add_multiple_blocks(self):
        """Test adding multiple different blocks to body."""
        content_page = ContentPage(
            title="Multiple Blocks Test",
            slug="multiple-blocks-test",
            locale=self.locale_en,
            body=[
                {"type": "heading", "value": "Introduction"},
                {"type": "paragraph", "value": "<p>First paragraph</p>"},
                {"type": "quote", "value": "A wise saying"},
                {"type": "paragraph", "value": "<p>Second paragraph</p>"},
            ],
        )
        self.home.add_child(instance=content_page)

        # Verify all blocks
        self.assertEqual(len(content_page.body), 4)
        self.assertEqual(content_page.body[0].block_type, "heading")
        self.assertEqual(content_page.body[1].block_type, "paragraph")
        self.assertEqual(content_page.body[2].block_type, "quote")
        self.assertEqual(content_page.body[3].block_type, "paragraph")

    def test_streamfield_uses_json_field(self):
        """Test that StreamField uses JSONField for storage."""
        # This is configured via use_json_field=True in the model
        content_page = ContentPage(
            title="JSON Test",
            slug="json-test",
            locale=self.locale_en,
            body=[
                {"type": "heading", "value": "Test"},
            ],
        )
        self.home.add_child(instance=content_page)

        # Refresh from DB
        content_page.refresh_from_db()

        # Should still have the block
        self.assertEqual(len(content_page.body), 1)
        self.assertEqual(content_page.body[0].value, "Test")


class ContentPageTranslationTests(WagtailPageTestCase):
    """Test translation functionality for ContentPage."""

    def setUp(self):
        """Set up test data with multiple locales."""
        # Create locales
        self.locale_en, _ = Locale.objects.get_or_create(language_code="en")
        self.locale_fi, _ = Locale.objects.get_or_create(language_code="fi")

        # Set up page tree
        self.root = Page.get_first_root_node()
        self.home_en = HomePage(
            title="Translation Test Home",
            slug="translation-test-home",
            locale=self.locale_en,
        )
        self.root.add_child(instance=self.home_en)

        # Create Finnish home page for translations to work
        self.home_fi = self.home_en.copy_for_translation(self.locale_fi)
        self.home_fi.title = "Käännöksen testikoti"
        self.home_fi.save()

    def test_content_page_is_translatable(self):
        """Test that ContentPage supports translations."""
        # Create English page
        page_en = ContentPage(
            title="English Content",
            slug="english-content",
            locale=self.locale_en,
            body=[
                {"type": "heading", "value": "Hello"},
                {"type": "paragraph", "value": "<p>Welcome to our site</p>"},
            ],
        )
        self.home_en.add_child(instance=page_en)

        # Create Finnish translation
        page_fi = page_en.copy_for_translation(self.locale_fi)
        page_fi.title = "Finnish Content"
        page_fi.body = [
            {"type": "heading", "value": "Terve"},
            {"type": "paragraph", "value": "<p>Tervetuloa sivuillemme</p>"},
        ]
        page_fi.save()

        # Verify both pages exist
        self.assertTrue(ContentPage.objects.filter(locale=self.locale_en).exists())
        self.assertTrue(ContentPage.objects.filter(locale=self.locale_fi).exists())

        # Verify they share a translation key
        self.assertEqual(page_en.translation_key, page_fi.translation_key)

    def test_can_get_translations(self):
        """Test retrieving translations of a page."""
        # Create English page
        page_en = ContentPage(
            title="Original Page",
            slug="original-page",
            locale=self.locale_en,
        )
        self.home_en.add_child(instance=page_en)

        # Create Finnish translation
        page_fi = page_en.copy_for_translation(self.locale_fi)
        page_fi.title = "Alkuperäinen Sivu"
        page_fi.save()

        # Get translations
        translations = page_en.get_translations(inclusive=False)
        self.assertEqual(translations.count(), 1)
        self.assertEqual(translations.first(), page_fi)

    def test_streamfield_content_translates_independently(self):
        """Test that StreamField content is independent per locale."""
        # Create English page
        page_en = ContentPage(
            title="English",
            slug="independent-content",
            locale=self.locale_en,
            body=[
                {"type": "paragraph", "value": "<p>English text</p>"},
            ],
        )
        self.home_en.add_child(instance=page_en)

        # Create Finnish translation with different content
        page_fi = page_en.copy_for_translation(self.locale_fi)
        page_fi.title = "Suomi"
        page_fi.body = [
            {"type": "paragraph", "value": "<p>Suomeksi teksti</p>"},
        ]
        page_fi.save()

        # Verify content is different
        self.assertNotEqual(page_en.body[0].value, page_fi.body[0].value)
        self.assertIn("English text", str(page_en.body[0].value))
        self.assertIn("Suomeksi teksti", str(page_fi.body[0].value))


class ContentPageTemplateTests(TestCase):
    """Test template rendering for ContentPage."""

    def setUp(self):
        """Set up test data."""
        self.locale_en, _ = Locale.objects.get_or_create(language_code="en")
        self.root = Page.get_first_root_node()
        self.home = HomePage(
            title="Template Test Home",
            slug="template-test-home",
            locale=self.locale_en,
        )
        self.root.add_child(instance=self.home)

        # Create site
        Site.objects.create(
            hostname="template-test.localhost",
            root_page=self.home,
            is_default_site=False,
            site_name="Template Test Site",
        )

    def test_content_page_has_template(self):
        """Test that ContentPage uses the correct template."""
        from django.test import RequestFactory

        content_page = ContentPage(
            title="Template Test",
            slug="template-test",
            locale=self.locale_en,
        )
        self.home.add_child(instance=content_page)

        # Create a mock request
        factory = RequestFactory()
        request = factory.get("/template-test/")

        # Default template should be content/content_page.html
        expected_template = "content/content_page.html"
        self.assertEqual(content_page.get_template(request), expected_template)

    def test_content_page_context(self):
        """Test that ContentPage provides correct context to template."""
        content_page = ContentPage(
            title="Context Test",
            slug="context-test",
            locale=self.locale_en,
            body=[
                {"type": "heading", "value": "Test Heading"},
            ],
        )
        self.home.add_child(instance=content_page)

        # Get context (requires a mock request)
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/context-test/")

        context = content_page.get_context(request)

        # Should include page in context
        self.assertIn("page", context)
        self.assertEqual(context["page"], content_page)


class ContentPageAdminTests(WagtailPageTestCase):
    """Test admin panel configuration for ContentPage."""

    def test_content_panels_includes_body(self):
        """Test that body field is in content panels."""
        # content_panels should include the body field
        panel_names = [
            panel.field_name
            for panel in ContentPage.content_panels
            if hasattr(panel, "field_name")
        ]
        self.assertIn("body", panel_names)

    def test_content_panels_includes_page_defaults(self):
        """Test that ContentPage includes default Page panels."""
        # Should include standard fields like title, slug, etc.
        # These come from Page.content_panels
        self.assertTrue(len(ContentPage.content_panels) > 1)


class ContentPageIntegrationTests(WagtailPageTestCase):
    """Integration tests for ContentPage with other apps."""

    def setUp(self):
        """Set up test data."""
        self.locale_en, _ = Locale.objects.get_or_create(language_code="en")
        self.root = Page.get_first_root_node()
        self.home = HomePage(
            title="Integration Test Home",
            slug="integration-test-home",
            locale=self.locale_en,
        )
        self.root.add_child(instance=self.home)

    def test_homepage_allows_content_page_children(self):
        """Test that HomePage configuration allows ContentPage."""
        self.assertIn("content.ContentPage", HomePage.subpage_types)

    def test_content_page_respects_homepage_constraints(self):
        """Test that ContentPage can be created under HomePage."""
        # This should work without raising validation errors
        content_page = ContentPage(
            title="Valid Child",
            slug="valid-child",
            locale=self.locale_en,
        )
        self.home.add_child(instance=content_page)

        # Verify it was created
        self.assertEqual(content_page.get_parent(), self.home)

    def test_content_page_tree_depth(self):
        """Test creating a deep hierarchy of ContentPages."""
        # Create a 3-level deep tree
        level1 = ContentPage(
            title="Level 1",
            slug="level-1",
            locale=self.locale_en,
        )
        self.home.add_child(instance=level1)

        level2 = ContentPage(
            title="Level 2",
            slug="level-2",
            locale=self.locale_en,
        )
        level1.add_child(instance=level2)

        level3 = ContentPage(
            title="Level 3",
            slug="level-3",
            locale=self.locale_en,
        )
        level2.add_child(instance=level3)

        # Verify hierarchy
        self.assertEqual(level1.get_parent(), self.home)
        self.assertEqual(level2.get_parent(), level1)
        self.assertEqual(level3.get_parent(), level2)
        self.assertEqual(level1.depth, self.home.depth + 1)
        self.assertEqual(level2.depth, level1.depth + 1)
        self.assertEqual(level3.depth, level2.depth + 1)
