"""
Management command to scaffold test navigation content.

Creates sample pages with navigation menus for testing the navigation system.
"""

from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Locale, Site

from content.models import ContentPage
from home.models import HomePage
from navigation.models import NavigationMenuSetting


class Command(BaseCommand):
    """Scaffold test navigation content with top-level and dropdown menu items."""

    help = "Creates sample pages (with dev_ prefix) and navigation menu for testing"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete existing scaffolded content before creating new",
        )
        parser.add_argument(
            "--skip-menu",
            action="store_true",
            help="Skip creating navigation menu (only create pages)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        try:
            # Get the default locale
            default_locale = Locale.get_default()

            # Get the site and its root page (should be HomePage)
            site = Site.objects.filter(is_default_site=True).first()
            if not site:
                raise CommandError(
                    "No default site found. Create a site in Wagtail Admin first.",
                )

            home_page = site.root_page.specific
            if not isinstance(home_page, HomePage):
                raise CommandError(
                    f"Site root page is {type(home_page).__name__}, not HomePage. "
                    "Please set a HomePage as the site root in Wagtail Admin.",
                )

            # Delete existing scaffolded content if requested
            if options["delete"]:
                self._delete_scaffolded_content(home_page)
                # Refresh home_page from database after tree fix
                home_page = type(home_page).objects.get(pk=home_page.pk)

            # Create sample pages
            pages = self._create_sample_pages(home_page, default_locale)

            # Create navigation menu if not skipped
            if not options["skip_menu"]:
                self._create_navigation_menu(pages, default_locale)

            self.stdout.write(
                self.style.SUCCESS("\n✅ Successfully scaffolded navigation content!"),
            )
            self.stdout.write("\nCreated pages:")
            for page in pages:
                self.stdout.write(f"  • {page.title} ({page.get_url()})")

            if not options["skip_menu"]:
                self.stdout.write(
                    "\n📋 Navigation menu configured in Wagtail Admin → Settings → Navigation",
                )

        except Exception as e:
            raise CommandError(f"Error scaffolding content: {e}")

    def _delete_scaffolded_content(self, home_page):
        """Delete previously scaffolded content."""
        self.stdout.write("Deleting existing scaffolded content...")

        # Define the slugs of pages created by this scaffold command
        # Prefixed with dev_ to avoid accidental deletion of production content
        SCAFFOLDED_SLUGS = (
            "dev_about",
            "dev_programs",
            "dev_contact",
        )

        # Query for only the scaffolded pages directly under home page
        deleted_count = 0
        scaffolded_pages = ContentPage.objects.filter(
            depth=home_page.depth + 1,
            path__startswith=home_page.path,
            slug__in=SCAFFOLDED_SLUGS,
        )

        for page in scaffolded_pages:
            # Delete the page and all its descendants (e.g., adult-education, youth-programs)
            # get_descendants() returns all descendant pages in the tree
            descendant_count = page.get_descendants().count()
            page.delete()  # This will cascade delete all descendants
            deleted_count += 1
            if descendant_count > 0:
                self.stdout.write(
                    f"  Deleted '{page.title}' and {descendant_count} descendant(s)",
                )

        if deleted_count > 0:
            self.stdout.write(
                self.style.WARNING(f"Deleted {deleted_count} scaffolded page(s)"),
            )

            # Fix the page tree after deletion to ensure consistency
            from django.core.management import call_command

            self.stdout.write("Fixing page tree structure...")
            call_command("fixtree", verbosity=0)
            self.stdout.write(self.style.SUCCESS("Page tree fixed"))

    def _create_sample_pages(self, home_page, locale):
        """Create sample pages for testing."""
        self.stdout.write("Creating sample pages...")

        pages = []

        # Top-level pages
        about_page = ContentPage(
            title="About",
            slug="dev_about",
            locale=locale,
            body=[
                {
                    "type": "heading",
                    "value": {"text": "About Us", "level": "h2"},
                },
                {
                    "type": "rich_text",
                    "value": "<p>Learn more about our Quaker community and values.</p>",
                },
            ],
        )
        home_page.add_child(instance=about_page)
        about_page.save_revision().publish()
        pages.append(about_page)

        programs_page = ContentPage(
            title="Programs",
            slug="dev_programs",
            locale=locale,
            body=[
                {
                    "type": "heading",
                    "value": {"text": "Our Programs", "level": "h2"},
                },
                {
                    "type": "rich_text",
                    "value": "<p>Explore our educational and community programs.</p>",
                },
            ],
        )
        home_page.add_child(instance=programs_page)
        programs_page.save_revision().publish()
        pages.append(programs_page)

        # Sub-pages under Programs (for dropdown testing)
        adult_education = ContentPage(
            title="Adult Education",
            slug="dev_adult-education",
            locale=locale,
            body=[
                {
                    "type": "heading",
                    "value": {"text": "Adult Education Programs", "level": "h2"},
                },
                {
                    "type": "rich_text",
                    "value": "<p>Educational opportunities for adults in our community.</p>",
                },
            ],
        )
        programs_page.add_child(instance=adult_education)
        adult_education.save_revision().publish()
        pages.append(adult_education)

        youth_programs = ContentPage(
            title="Youth Programs",
            slug="dev_youth-programs",
            locale=locale,
            body=[
                {
                    "type": "heading",
                    "value": {"text": "Youth Programs", "level": "h2"},
                },
                {
                    "type": "rich_text",
                    "value": "<p>Programs and activities for young people.</p>",
                },
            ],
        )
        programs_page.add_child(instance=youth_programs)
        youth_programs.save_revision().publish()
        pages.append(youth_programs)

        # Additional top-level page
        contact_page = ContentPage(
            title="Contact",
            slug="dev_contact",
            locale=locale,
            body=[
                {
                    "type": "heading",
                    "value": {"text": "Contact Us", "level": "h2"},
                },
                {
                    "type": "rich_text",
                    "value": "<p>Get in touch with our community.</p>",
                },
            ],
        )
        home_page.add_child(instance=contact_page)
        contact_page.save_revision().publish()
        pages.append(contact_page)

        self.stdout.write(self.style.SUCCESS(f"Created {len(pages)} pages"))
        return pages

    def _create_navigation_menu(self, pages, locale):
        """Create navigation menu configuration."""
        self.stdout.write("Configuring navigation menu...")

        # Get the default site
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stdout.write(
                self.style.WARNING("No default site found, skipping navigation menu"),
            )
            return

        # Get or create NavigationMenuSetting for the site
        nav_settings = NavigationMenuSetting.for_site(site)

        # Find pages by title
        about_page = next((p for p in pages if p.title == "About"), None)
        programs_page = next((p for p in pages if p.title == "Programs"), None)
        adult_ed_page = next((p for p in pages if p.title == "Adult Education"), None)
        youth_page = next((p for p in pages if p.title == "Youth Programs"), None)
        contact_page = next((p for p in pages if p.title == "Contact"), None)

        # Build navigation menu structure
        # Note: PageLinkBlock is a StructBlock with 'page', 'custom_title', and 'anchor' fields
        nav_settings.menu_items = [
            {
                "type": "page_link",
                "value": {
                    "page": about_page.id if about_page else None,
                    "custom_title": "",
                    "anchor": "",
                },
                "id": "about-link",
            },
            {
                "type": "dropdown",
                "value": {
                    "title": "Programs",
                    "items": [
                        {
                            "type": "page_link",
                            "value": {
                                "page": programs_page.id if programs_page else None,
                                "custom_title": "",
                                "anchor": "",
                            },
                            "id": "programs-overview-link",
                        },
                        {
                            "type": "page_link",
                            "value": {
                                "page": adult_ed_page.id if adult_ed_page else None,
                                "custom_title": "",
                                "anchor": "",
                            },
                            "id": "adult-ed-link",
                        },
                        {
                            "type": "page_link",
                            "value": {
                                "page": youth_page.id if youth_page else None,
                                "custom_title": "",
                                "anchor": "",
                            },
                            "id": "youth-link",
                        },
                    ],
                },
                "id": "programs-dropdown",
            },
            {
                "type": "external_link",
                "value": {
                    "url": "https://www.fgcquaker.org/",
                    "title": "FGC Website",
                    "anchor": "",
                },
                "id": "fgc-link",
            },
            {
                "type": "page_link",
                "value": {
                    "page": contact_page.id if contact_page else None,
                    "custom_title": "",
                    "anchor": "",
                },
                "id": "contact-link",
            },
        ]

        nav_settings.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated NavigationMenuSetting for site: {site.site_name}",
            ),
        )
