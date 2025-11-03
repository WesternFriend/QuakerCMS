# Quickstart: Navigation Menu System

**Last Updated**: 2025-10-26
**For**: Developers implementing the navigation menu feature

## Overview

This guide provides step-by-step instructions for implementing the multi-lingual navigation menu system in QuakerCMS. Follow these steps in order.

## Prerequisites

- QuakerCMS development environment set up (see project README)
- Python 3.12+, Django 5.2+, Wagtail 7.0+
- Basic understanding of Wagtail StreamFields and Django templates
- Access to run migrations and modify settings

## Implementation Steps

### Step 1: Create Navigation App

```bash
cd src
python manage.py startapp navigation
```

### Step 2: Add to INSTALLED_APPS

Edit `src/core/settings/base.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'navigation',  # Add this
    # ... rest of apps ...
]
```

### Step 3: Create StreamField Blocks

Create `src/navigation/blocks.py`:

```python
from wagtail.blocks import StructBlock, CharBlock, URLBlock, StreamBlock, PageChooserBlock


class PageLinkBlock(StructBlock):
    """Internal page link with optional custom title."""
    page = PageChooserBlock(
        required=True,
        help_text="Select a page to link to"
    )
    custom_title = CharBlock(
        required=False,
        max_length=100,
        help_text="Override the page title (leave blank to use page's own title)"
    )
    anchor = CharBlock(
        required=False,
        max_length=50,
        help_text="Optional anchor (e.g., 'section-name' for #section-name)"
    )

    class Meta:
        icon = 'doc-full'
        label = 'Page Link'


class ExternalLinkBlock(StructBlock):
    """External URL link."""
    url = URLBlock(
        required=True,
        help_text="Full URL including http:// or https://"
    )
    title = CharBlock(
        required=True,
        max_length=100,
        help_text="Link text to display in menu"
    )
    anchor = CharBlock(
        required=False,
        max_length=50,
        help_text="Optional anchor (e.g., 'section' for #section)"
    )

    class Meta:
        icon = 'link'
        label = 'External Link'


class MenuItemBlock(StreamBlock):
    """Items within a dropdown - only simple links allowed."""
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    # NOTE: No DropdownMenuBlock here - enforces 2-level maximum

    class Meta:
        icon = 'link'
        label = 'Menu Item'
        max_num = 20


class DropdownMenuBlock(StructBlock):
    """Dropdown menu with child items."""
    title = CharBlock(
        required=True,
        max_length=100,
        help_text="Dropdown menu label"
    )
    items = MenuItemBlock(
        required=True,
        help_text="Links to display in dropdown menu"
    )

    class Meta:
        icon = 'list-ul'
        label = 'Dropdown Menu'


class TopLevelMenuBlock(StreamBlock):
    """Top-level menu items - can be links OR dropdowns."""
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    dropdown = DropdownMenuBlock()

    class Meta:
        icon = 'list-ul'
        label = 'Navigation Menu'
        max_num = 10
```

### Step 4: Create Model

Create `src/navigation/models.py`:

```python
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel


@register_setting
class NavigationMenuSetting(BaseSiteSetting):
    """Site-wide navigation menu configuration."""

    menu_items = StreamField(
        'navigation.TopLevelMenuBlock',
        blank=True,
        use_json_field=True,
        help_text="Configure the main navigation menu for your site."
    )

    panels = [
        FieldPanel('menu_items'),
    ]

    class Meta:
        verbose_name = "Navigation Menu"
        verbose_name_plural = "Navigation Menu"
```

### Step 5: Create Template Tag

Create `src/navigation/templatetags/` directory and `__init__.py`:

```bash
mkdir -p src/navigation/templatetags
touch src/navigation/templatetags/__init__.py
```

Create `src/navigation/templatetags/navigation_tags.py`:

```python
from django import template
from wagtail.models import Locale, Page

register = template.Library()


@register.inclusion_tag('navigation/navigation.html', takes_context=True)
def navigation_menu(context):
    """Render navigation menu with locale-aware page links."""
    request = context['request']
    current_locale = Locale.get_active()
    default_locale = Locale.get_default()

    # Get menu settings
    from navigation.models import NavigationMenuSetting
    menu_settings = NavigationMenuSetting.for_request(request)

    if not menu_settings or not menu_settings.menu_items:
        return {'menu_items': []}

    # Process menu items
    processed_items = []
    for item in menu_settings.menu_items:
        processed_item = process_menu_item(item, current_locale, default_locale, context.get('page'))
        if processed_item:
            processed_items.append(processed_item)

    return {
        'menu_items': processed_items,
        'current_page': context.get('page'),
        'request': request,
    }


def process_menu_item(item, current_locale, default_locale, current_page=None):
    """Convert menu item to locale-specific version."""
    item_type = item.block_type

    if item_type == 'page_link':
        page = item.value.get('page')

        if not page or not page.live:
            return None

        # Try to get page translation
        try:
            localized_page = page.localized.get(locale=current_locale)
        except Page.DoesNotExist:
            try:
                localized_page = page.localized.get(locale=default_locale)
            except Page.DoesNotExist:
                return None

        anchor = item.value.get('anchor', '')
        url = localized_page.url
        if anchor:
            url += f'#{anchor}'

        return {
            'type': 'page_link',
            'page': localized_page,
            'url': url,
            'title': item.value.get('custom_title') or localized_page.title,
            'is_current': current_page and current_page.id == localized_page.id,
        }

    elif item_type == 'external_link':
        anchor = item.value.get('anchor', '')
        url = item.value['url']
        if anchor:
            url += f'#{anchor}'

        return {
            'type': 'external_link',
            'url': url,
            'title': item.value['title'],
            'is_current': False,
        }

    elif item_type == 'dropdown':
        child_items = []
        has_current = False

        for child in item.value.get('items', []):
            processed_child = process_menu_item(child, current_locale, default_locale, current_page)
            if processed_child:
                child_items.append(processed_child)
                if processed_child.get('is_current'):
                    has_current = True

        if child_items:
            return {
                'type': 'dropdown',
                'title': item.value['title'],
                'items': child_items,
                'is_open': has_current,
            }

    return None
```

### Step 6: Create Templates

Create template directory structure:

```bash
mkdir -p src/navigation/templates/navigation
```

Create `src/navigation/templates/navigation/navigation.html`:

```django
{% load static %}

{% if menu_items %}
<div class="drawer lg:drawer-open">
  {# Checkbox for mobile drawer state #}
  <input id="nav-drawer" type="checkbox" class="drawer-toggle" />

  <div class="drawer-content flex flex-col">
    {# Desktop Navigation #}
    <nav class="navbar bg-base-100 hidden lg:flex" aria-label="Main navigation">
      <div class="flex-1">
        <ul class="menu menu-horizontal" role="menubar">
          {% for item in menu_items %}
            {% if item.type == 'page_link' or item.type == 'external_link' %}
              <li role="none">
                <a
                  href="{{ item.url }}"
                  role="menuitem"
                  {% if item.is_current %}aria-current="page" class="active"{% endif %}
                >
                  {{ item.title }}
                </a>
              </li>
            {% elif item.type == 'dropdown' %}
              <li role="none" class="dropdown dropdown-hover">
                <button
                  role="menuitem"
                  aria-haspopup="true"
                  aria-expanded="false"
                  class="btn btn-ghost"
                >
                  {{ item.title }}
                  <svg class="fill-current" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"><path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z"/></svg>
                </button>
                <ul role="menu" class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
                  {% for child in item.items %}
                    <li role="none">
                      <a
                        href="{{ child.url }}"
                        role="menuitem"
                        {% if child.is_current %}aria-current="page" class="active"{% endif %}
                      >
                        {{ child.title }}
                      </a>
                    </li>
                  {% endfor %}
                </ul>
              </li>
            {% endif %}
          {% endfor %}
        </ul>
      </div>
    </nav>

    {# Mobile Hamburger Button #}
    <div class="navbar bg-base-100 lg:hidden">
      <label
        for="nav-drawer"
        class="btn btn-square btn-ghost"
        aria-label="Open menu"
        aria-expanded="false"
        aria-controls="mobile-menu"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
      </label>
    </div>

    {# Main content slot #}
    <div class="flex-1">
      {# Page content will be rendered here by base template #}
    </div>
  </div>

  {# Mobile Drawer #}
  <div class="drawer-side lg:hidden">
    <label for="nav-drawer" class="drawer-overlay" aria-label="Close menu"></label>

    <aside id="mobile-menu" class="min-h-full w-80 bg-base-200">
      {# Close button #}
      <div class="flex justify-end p-4">
        <label for="nav-drawer" class="btn btn-sm btn-circle btn-ghost" aria-label="Close menu">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </label>
      </div>

      {# Mobile menu items #}
      <ul class="menu p-4 w-full" role="menu">
        {% for item in menu_items %}
          {% if item.type == 'page_link' or item.type == 'external_link' %}
            <li role="none">
              <a
                href="{{ item.url }}"
                role="menuitem"
                {% if item.is_current %}aria-current="page" class="active"{% endif %}
              >
                {{ item.title }}
              </a>
            </li>
          {% elif item.type == 'dropdown' %}
            <li role="none">
              <details {% if item.is_open %}open{% endif %}>
                <summary role="menuitem" aria-haspopup="true">
                  {{ item.title }}
                </summary>
                <ul role="menu">
                  {% for child in item.items %}
                    <li role="none">
                      <a
                        href="{{ child.url }}"
                        role="menuitem"
                        {% if child.is_current %}aria-current="page" class="active"{% endif %}
                      >
                        {{ child.title }}
                      </a>
                    </li>
                  {% endfor %}
                </ul>
              </details>
            </li>
          {% endif %}
        {% endfor %}
      </ul>
    </aside>
  </div>
</div>
{% endif %}
```

### Step 7: Update Base Template

Edit `src/core/templates/base.html` to include skip link and navigation:

```django
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    <!-- head content -->
</head>
<body>
    {# Skip link for accessibility #}
    <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:p-4 focus:bg-primary focus:text-primary-content">
        Skip to main content
    </a>

    {# Navigation menu #}
    {% load navigation_tags %}
    {% navigation_menu %}

    {# Main content #}
    <main id="main-content" tabindex="-1">
        {% block content %}{% endblock %}
    </main>

    <!-- footer, scripts, etc. -->
</body>
</html>
```

### Step 8: Create and Run Migrations

```bash
cd src
python manage.py makemigrations navigation
python manage.py migrate navigation
```

### Step 9: Configure Menu in Admin

1. Start development server: `python manage.py runserver`
2. Log in to Wagtail admin: http://localhost:8000/admin/
3. Navigate to **Settings** → **Navigation Menu**
4. Click **Add menu item** to add links or dropdowns
5. Save changes

### Step 10: Verify Installation

1. Visit your site homepage
2. Verify navigation menu appears in header
3. Test mobile view (resize browser to <1024px)
4. Verify hamburger menu opens with drawer
5. Test keyboard navigation (Tab, Enter, Escape keys)
6. Test screen reader (if available): Check ARIA announcements

## Testing

Create `src/navigation/tests.py`:

```python
from django.test import TestCase
from wagtail.models import Locale, Site
from wagtail.test.utils import WagtailTestUtils
from navigation.models import NavigationMenuSetting
from home.models import HomePage


class NavigationMenuTests(WagtailTestUtils, TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.locale = Locale.get_default()

        # Create test pages
        self.home = HomePage.objects.first()
        self.about_page = HomePage(
            title="About",
            slug="about",
            locale=self.locale,
        )
        self.home.add_child(instance=self.about_page)
        self.about_page.save_revision().publish()

    def test_create_navigation_menu(self):
        """Can create navigation menu setting."""
        menu = NavigationMenuSetting.objects.create(
            site=self.site,
            menu_items=[
                {
                    'type': 'page_link',
                    'value': {
                        'page': self.about_page.id,
                        'custom_title': '',
                        'anchor': '',
                    },
                },
            ],
        )
        self.assertEqual(len(menu.menu_items), 1)
```

Run tests:

```bash
cd src
python manage.py test navigation
```

## Troubleshooting

### Menu Not Appearing

**Problem**: Navigation doesn't show on site

**Solutions**:
1. Check `navigation` is in `INSTALLED_APPS`
2. Verify migrations ran: `python manage.py migrate navigation`
3. Check menu is configured in Settings → Navigation Menu
4. Ensure `{% load navigation_tags %}` is in template
5. Verify `{% navigation_menu %}` tag is in base template

### Dropdown Not Working

**Problem**: Dropdowns don't open on click/hover

**Solutions**:
1. Check DaisyUI classes are correct (`dropdown dropdown-hover`)
2. Verify Tailwind CSS is compiled: `cd src/theme/static_src && npm run dev`
3. Check browser console for JavaScript errors
4. Test with different browsers (CSS-only version should work)

### Deleted Pages Still Show

**Problem**: Menu shows links to deleted pages

**Solutions**:
1. Template tag should filter these automatically - check `process_menu_item()` logic
2. Verify pages are actually deleted (not just unpublished)
3. Clear browser cache
4. Restart development server

### Mobile Menu Not Sliding

**Problem**: Drawer doesn't open on mobile

**Solutions**:
1. Check drawer checkbox has correct `id="nav-drawer"`
2. Verify label `for` attribute matches checkbox ID
3. Ensure DaisyUI is installed and compiled
4. Test viewport width is actually < 1024px

### Accessibility Errors

**Problem**: WCAG validation fails

**Solutions**:
1. Run axe DevTools scan to identify specific issues
2. Check all ARIA attributes match contract specification
3. Verify focus indicators are visible (test with Tab key)
4. Ensure skip link works (Tab key on page load)

## Next Steps

- **Phase 2**: Implement tasks (see `/speckit.tasks` command output)
- **Testing**: Write comprehensive test suite (ModelTests, StreamFieldTests, AdminTests, IntegrationTests)
- **Accessibility**: Run WCAG validation and manual screen reader testing
- **Performance**: Add caching if needed for high-traffic sites
- **Documentation**: Update AGENTS.md with navigation patterns

## Resources

- [Wagtail StreamField Documentation](https://docs.wagtail.org/en/stable/topics/streamfield.html)
- [DaisyUI Drawer Component](https://daisyui.com/components/drawer/)
- [WAI-ARIA Authoring Practices - Menubar](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)

## Support

For questions or issues:
1. Check existing tests for examples
2. Review AGENTS.md for architecture guidance
3. Search Wagtail documentation for StreamField patterns
4. Open GitHub issue with specific error messages
