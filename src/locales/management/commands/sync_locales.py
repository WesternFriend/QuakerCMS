"""
Management command to sync Wagtail Locale model with LocaleSettings.

This command creates Locale records for all languages configured in LocaleSettings
and optionally removes unused locales that have no associated content.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Locale, Page

from locales.models import LocaleSettings


class Command(BaseCommand):
    help = "Sync Wagtail Locale model with LocaleSettings configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--remove-unused",
            action="store_true",
            help="Remove locales that have no associated pages or snippets",
        )

    def handle(self, *args, **options):
        self.stdout.write("Syncing locales with LocaleSettings...")

        # Get all locale settings
        locale_settings = LocaleSettings.objects.all()

        if not locale_settings.exists():
            self.stdout.write(
                self.style.WARNING(
                    "No LocaleSettings found. Please configure locale settings first.",
                ),
            )
            return

        # Collect all desired language codes
        desired_languages = set()
        for settings in locale_settings:
            if settings.available_languages:
                desired_languages.update(settings.available_languages)

        if not desired_languages:
            self.stdout.write(
                self.style.WARNING("No languages configured in LocaleSettings."),
            )
            return

        # Get existing locale codes
        existing_locales = {
            locale.language_code: locale for locale in Locale.objects.all()
        }

        # Create missing locales
        created_count = 0
        for language_code in desired_languages:
            if language_code not in existing_locales:
                Locale.objects.create(language_code=language_code)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created locale: {language_code}"),
                )
                created_count += 1

        if created_count == 0:
            self.stdout.write("No new locales needed to be created.")

        # Optionally remove unused locales
        if options["remove_unused"]:
            self.stdout.write("\nChecking for unused locales...")
            removed_count = 0

            for language_code, locale in existing_locales.items():
                if language_code not in desired_languages:
                    # Check if locale has any content
                    page_count = Page.objects.filter(locale=locale).count()

                    if page_count > 0:
                        self.stdout.write(
                            self.style.WARNING(
                                f"✗ Cannot remove {language_code}: "
                                f"has {page_count} associated page(s)",
                            ),
                        )
                    else:
                        locale.delete()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Removed unused locale: {language_code}",
                            ),
                        )
                        removed_count += 1

            if removed_count == 0:
                self.stdout.write("No unused locales to remove.")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Sync complete! Active locales: {', '.join(sorted(desired_languages))}",
            ),
        )
