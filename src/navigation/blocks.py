"""Navigation menu blocks for QuakerCMS.

This module defines the StreamField blocks used for building navigation menus.
The blocks enforce a maximum 2-level nesting structure through their schema:
- Top level can contain page links, external links, or dropdowns
- Dropdown items can only contain page links or external links (no nested dropdowns)

Note: These blocks do not use Meta.template for rendering. Instead, rendering is
handled by the navigation_menu template tag in navigation/templatetags/navigation_tags.py.
This centralizes rendering logic and makes it easier to maintain desktop/mobile variations.
"""

from django.core.exceptions import ValidationError
from wagtail import blocks


class PageLinkBlock(blocks.StructBlock):
    """Internal page link with optional custom title."""

    page = blocks.PageChooserBlock(
        required=True,
        help_text="Select a page to link to",
    )
    custom_title = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text="Override the page title (leave blank to use page's own title)",
    )
    anchor = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text="Optional anchor (e.g., 'section-name' for #section-name)",
    )

    class Meta:
        icon = "doc-full"
        label = "Page Link"


class ExternalLinkBlock(blocks.StructBlock):
    """External URL link."""

    url = blocks.URLBlock(
        required=True,
        help_text="Full URL including http:// or https://",
    )
    title = blocks.CharBlock(
        required=True,
        max_length=100,
        help_text="Link text to display in menu",
    )
    anchor = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text="Optional anchor (e.g., 'section' for #section)",
    )

    class Meta:
        icon = "link"
        label = "External Link"


class MenuItemBlock(blocks.StreamBlock):
    """Items within a dropdown - only simple links allowed (enforces 2-level maximum)."""

    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    # NOTE: No DropdownMenuBlock here - prevents 3rd level nesting

    class Meta:
        icon = "link"
        label = "Menu Item"
        max_num = 20  # Reasonable limit per dropdown


class DropdownMenuBlock(blocks.StructBlock):
    """Dropdown menu with child items."""

    title = blocks.CharBlock(
        required=True,
        max_length=100,
        help_text="Dropdown menu label",
    )
    items = MenuItemBlock(
        help_text="Links to display in dropdown menu",
    )

    def clean(self, value):
        """Validate that dropdown contains at least one item."""
        # Call parent clean first to get cleaned values
        try:
            cleaned = super().clean(value)
        except blocks.StructBlockValidationError:
            # If parent validation fails, provide our custom message
            raise ValidationError("Dropdown menu must contain at least one item")

        # Double-check if items list is empty
        items = cleaned.get("items") if cleaned else []
        if not items:
            raise ValidationError("Dropdown menu must contain at least one item")

        return cleaned

    class Meta:
        icon = "list-ul"
        label = "Dropdown Menu"


class TopLevelMenuBlock(blocks.StreamBlock):
    """Top-level menu items - can be links OR dropdowns."""

    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    dropdown = DropdownMenuBlock()

    class Meta:
        icon = "list-ul"
        label = "Navigation Menu"
        max_num = 10  # Reasonable limit for usability
