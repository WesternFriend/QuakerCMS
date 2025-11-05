"""App configuration for navigation menu system."""

from django.apps import AppConfig


class NavigationConfig(AppConfig):
    """Configuration for the navigation app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "navigation"
    verbose_name = "Navigation Menu"
