"""Template tags for navigation menu rendering."""

from django import template
from wagtail.models import Locale, Page

from navigation.models import NavigationMenuSetting

register = template.Library()


def _collect_page_ids(item, page_ids):
    """Recursively collect all page IDs from menu structure."""
    if item.block_type == "page_link":
        page = item.value.get("page")
        if page:
            page_ids.append(page.id)
    elif item.block_type == "dropdown":
        for child in item.value.get("items", []):
            _collect_page_ids(child, page_ids)


@register.inclusion_tag("navigation/navigation.html", takes_context=True)
def navigation_menu(context):
    """Render navigation menu with locale-aware page links."""
    request = context["request"]
    current_locale = Locale.get_active()
    default_locale = Locale.get_default()

    # Get menu settings
    menu_settings = NavigationMenuSetting.for_request(request)

    if not menu_settings or not menu_settings.menu_items:
        return {"menu_items": []}

    # Collect all page IDs upfront
    page_ids = []
    for item in menu_settings.menu_items:
        _collect_page_ids(item, page_ids)

    # Prefetch all pages with their translations in one query
    pages_cache = {}
    if page_ids:
        # Fetch pages and prefetch their locale relations
        # Note: We can't prefetch translations directly, so we fetch all locales
        # and let get_translation() handle the lookup efficiently
        pages = Page.objects.filter(id__in=page_ids).select_related("locale")
        for page in pages:
            pages_cache[page.id] = page

    # Process menu items with cached pages
    processed_items = []
    for item in menu_settings.menu_items:
        processed_item = process_menu_item(
            item,
            current_locale,
            default_locale,
            context.get("page"),
            pages_cache,
        )
        if processed_item:
            processed_items.append(processed_item)

    return {
        "menu_items": processed_items,
        "current_page": context.get("page"),
        "request": request,
    }


def process_menu_item(
    item,
    current_locale,
    default_locale,
    current_page=None,
    pages_cache=None,
):
    """Convert menu item to locale-specific version.

    Args:
        item: Menu item block from NavigationMenuSetting
        current_locale: Current active locale
        default_locale: Default fallback locale
        current_page: Current page for highlighting active items
        pages_cache: Dict mapping page IDs to prefetched Page objects (optional)
    """
    item_type = item.block_type

    if item_type == "page_link":
        page = item.value.get("page")

        if not page or not page.live:
            return None

        # Use cached page if available (already has prefetched translations)
        if pages_cache and page.id in pages_cache:
            page = pages_cache[page.id]

        # Try to get page translation
        try:
            localized_page = page.get_translation(current_locale)
        except (Page.DoesNotExist, AttributeError):
            try:
                localized_page = page.get_translation(default_locale)
            except (Page.DoesNotExist, AttributeError):
                # If page doesn't exist in any locale or doesn't support translations,
                # use the original page
                localized_page = page

        anchor = item.value.get("anchor", "")
        url = localized_page.url
        if anchor:
            url += f"#{anchor}"

        return {
            "type": "page_link",
            "page": localized_page,
            "url": url,
            "title": item.value.get("custom_title") or localized_page.title,
            "is_current": current_page and current_page.id == localized_page.id,
        }

    elif item_type == "external_link":
        anchor = item.value.get("anchor", "")
        url = item.value["url"]
        if anchor:
            url += f"#{anchor}"

        return {
            "type": "external_link",
            "url": url,
            "title": item.value["title"],
            "is_current": False,
        }

    elif item_type == "dropdown":
        child_items = []
        has_current = False

        for child in item.value.get("items", []):
            processed_child = process_menu_item(
                child,
                current_locale,
                default_locale,
                current_page,
                pages_cache,
            )
            if processed_child:
                child_items.append(processed_child)
                if processed_child.get("is_current"):
                    has_current = True

        # Only include dropdown if it has at least one valid child
        if child_items:
            return {
                "type": "dropdown",
                "title": item.value["title"],
                "items": child_items,
                "is_open": has_current,
            }

    return None
