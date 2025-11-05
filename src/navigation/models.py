"""Models for navigation menu system."""

from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField

from navigation.blocks import TopLevelMenuBlock


@register_setting
class NavigationMenuSetting(BaseSiteSetting):
    """Site-wide navigation menu configuration."""

    menu_items = StreamField(
        TopLevelMenuBlock(),
        blank=True,
        use_json_field=True,
        help_text="Configure the main navigation menu for your site.",
    )

    panels = [
        FieldPanel("menu_items"),
    ]

    class Meta:
        verbose_name = "Navigation Menu"
        verbose_name_plural = "Navigation Menu"
