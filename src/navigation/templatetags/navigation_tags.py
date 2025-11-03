"""Template tags for navigation menu rendering."""

from django import template
from wagtail.models import Locale, Page

from navigation.models import NavigationMenuSetting

register = template.Library()


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

    # Process menu items
    processed_items = []
    for item in menu_settings.menu_items:
        processed_item = process_menu_item(
            item,
            current_locale,
            default_locale,
            context.get("page"),
        )
        if processed_item:
            processed_items.append(processed_item)

    return {
        "menu_items": processed_items,
        "current_page": context.get("page"),
        "request": request,
    }


def process_menu_item(item, current_locale, default_locale, current_page=None):
    """Convert menu item to locale-specific version."""
    item_type = item.block_type

    if item_type == "page_link":
        page = item.value.get("page")

        if not page or not page.live:
            return None

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
