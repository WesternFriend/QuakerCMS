"""StreamField blocks for navigation menu system."""

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
        required=True,
        help_text="Links to display in dropdown menu",
    )

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
