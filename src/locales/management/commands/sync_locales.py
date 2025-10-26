"""
Management command to sync Wagtail Locale model with LocaleSettings.

This command creates Locale records for all languages configured in LocaleSettings
and optionally removes unused locales that have no associated content.
"""

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models
from wagtail.models import Locale

from locales.models import LocaleSettings


class Command(BaseCommand):
    help = "Sync Wagtail Locale model with LocaleSettings configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--remove-unused",
            action="store_true",
            help="Remove locales that have no associated content in any translatable model",
        )

    def get_translatable_models(self):
        """
        Get all models that have a locale ForeignKey field.

        Returns:
            list: List of model classes that are translatable
        """
        translatable_models = []
        for model in apps.get_models():
            # Check if model has a 'locale' field that's a ForeignKey
            for field in model._meta.get_fields():
                if (
                    field.name == "locale"
                    and isinstance(field, models.ForeignKey)
                    and field.related_model == Locale
                ):
                    translatable_models.append(model)
                    break
        return translatable_models

    def get_locale_usage(self, locale):
        """
        Check all translatable models for usage of a specific locale.

        Args:
            locale: The Locale instance to check

        Returns:
            dict: Dictionary mapping model names to counts of objects using this locale
        """
        usage = {}
        translatable_models = self.get_translatable_models()

        for model in translatable_models:
            count = model.objects.filter(locale=locale).count()
            if count > 0:
                model_name = f"{model._meta.app_label}.{model.__name__}"
                usage[model_name] = count

        return usage

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
                    # Check if locale has any content in any translatable model
                    usage = self.get_locale_usage(locale)

                    if usage:
                        # Locale is in use - cannot delete
                        total_count = sum(usage.values())
                        self.stdout.write(
                            self.style.WARNING(
                                f"✗ Cannot remove {language_code}: "
                                f"{total_count} related object(s) exist",
                            ),
                        )
                        # Log which models are using this locale
                        for model_name, count in sorted(usage.items()):
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  - {model_name}: {count} object(s)",
                                ),
                            )
                    else:
                        # No related objects - safe to delete
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
