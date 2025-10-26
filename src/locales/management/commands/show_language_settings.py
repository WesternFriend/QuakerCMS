"""
Management command to display current language settings.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.models import Site

from core.constants import DEFAULT_LANGUAGE_CODE, DEFAULT_LANGUAGES
from locales.models import LocaleSettings


class Command(BaseCommand):
    help = "Display current language settings from LocaleSettings"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Language Settings ===\n"))

        # Show default fallbacks
        self.stdout.write("Default Fallbacks:")
        self.stdout.write(f"  DEFAULT_LANGUAGE_CODE: {DEFAULT_LANGUAGE_CODE}")
        self.stdout.write(f"  DEFAULT_LANGUAGES: {DEFAULT_LANGUAGES}\n")

        # Show current settings
        self.stdout.write("Current Django Settings:")
        self.stdout.write(f"  LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
        self.stdout.write(f"  LANGUAGES: {settings.LANGUAGES}")
        self.stdout.write(
            f"  WAGTAIL_CONTENT_LANGUAGES: {settings.WAGTAIL_CONTENT_LANGUAGES}\n",
        )

        # Show per-site settings from database
        self.stdout.write("LocaleSettings (from database):")
        sites = Site.objects.all()

        if not sites:
            self.stdout.write(self.style.WARNING("  No sites found in database"))
            return

        for site in sites:
            locale_settings = LocaleSettings.objects.filter(site=site).first()

            if locale_settings:
                default_marker = " [DEFAULT]" if site.is_default_site else ""
                self.stdout.write(
                    f"\n  Site: {site.hostname}:{site.port}{default_marker}",
                )
                self.stdout.write(
                    f"    Default Language: {locale_settings.default_language}",
                )
                self.stdout.write(
                    f"    Available Languages: {locale_settings.available_languages}",
                )
                self.stdout.write(
                    f"    Languages List: {locale_settings.get_available_languages_list()}",
                )
            else:
                default_marker = " [DEFAULT]" if site.is_default_site else ""
                self.stdout.write(
                    f"\n  Site: {site.hostname}:{site.port}{default_marker}",
                )
                self.stdout.write(
                    self.style.WARNING(
                        "    No LocaleSettings configured (using defaults)",
                    ),
                )
