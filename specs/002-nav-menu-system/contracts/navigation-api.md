# Navigation API Contract

**Date**: 2025-10-26
**Version**: 1.0.0

## Overview

This document defines the contract between the navigation system backend (template tags, models) and frontend templates. It specifies the data structures, template context variables, and rendering expectations.

## Template Tag API

### `{% navigation_menu %}`

**Purpose**: Renders the site-wide navigation menu with locale-aware page links and accessibility features.

**Usage**:

```django
{% load navigation_tags %}
{% navigation_menu %}
```

**Context Variables Provided**:

| Variable       | Type         | Description                             |
| -------------- | ------------ | --------------------------------------- |
| `menu_items`   | List[Dict]   | Processed menu items for current locale |
| `current_page` | Page \| None | Current page object (if available)      |
| `request`      | HttpRequest  | Request object for locale detection     |

**Template**: `navigation/navigation.html`

**Behavior**:

- Returns empty dict if no menu configured (template renders nothing)
- Filters out deleted/unpublished pages automatically
- Resolves pages to current locale with fallback to default
- Marks current page with `is_current=True` flag

---

## Data Structures

### MenuItem (Processed)

After processing by template tag, each menu item is a dictionary with the following structure:

#### PageLink Item

```python
{
    'type': 'page_link',
    'page': Page,              # Wagtail Page object (localized)
    'url': str,                # Full URL path (e.g., '/en/about/')
    'title': str,              # Display title (custom or page title)
    'anchor': str,             # Fragment identifier (e.g., 'section')
    'is_current': bool,        # True if this page matches current request
}
```

#### ExternalLink Item

```python
{
    'type': 'external_link',
    'url': str,                # Full URL (e.g., 'https://example.com/docs')
    'title': str,              # Display title from menu config
    'anchor': str,             # Fragment identifier (if any)
    'is_current': bool,        # Always False for external links
}
```

#### Dropdown Item

```python
{
    'type': 'dropdown',
    'title': str,              # Dropdown menu label
    'items': List[Dict],       # Child items (PageLink or ExternalLink)
    'is_open': bool,           # True if any child is current page
}
```

---

## Template Context Examples

### Basic Menu (3 top-level links)

```python
{
    'menu_items': [
        {
            'type': 'page_link',
            'page': <Page: About>,
            'url': '/en/about/',
            'title': 'About Us',
            'anchor': '',
            'is_current': False,
        },
        {
            'type': 'page_link',
            'page': <Page: Contact>,
            'url': '/en/contact/',
            'title': 'Contact',
            'anchor': '',
            'is_current': True,  # User is on contact page
        },
        {
            'type': 'external_link',
            'url': 'https://docs.example.com',
            'title': 'Documentation',
            'anchor': '',
            'is_current': False,
        },
    ],
    'current_page': <Page: Contact>,
    'request': <HttpRequest>,
}
```

### Nested Menu (with dropdown)

```python
{
    'menu_items': [
        {
            'type': 'page_link',
            'page': <Page: Home>,
            'url': '/en/',
            'title': 'Home',
            'anchor': '',
            'is_current': False,
        },
        {
            'type': 'dropdown',
            'title': 'Resources',
            'items': [
                {
                    'type': 'page_link',
                    'page': <Page: Guides>,
                    'url': '/en/resources/guides/',
                    'title': 'User Guides',
                    'anchor': '',
                    'is_current': True,  # User is on guides page
                },
                {
                    'type': 'page_link',
                    'page': <Page: Videos>,
                    'url': '/en/resources/videos/',
                    'title': 'Videos',
                    'anchor': '',
                    'is_current': False,
                },
                {
                    'type': 'external_link',
                    'url': 'https://api.example.com/docs',
                    'title': 'API Reference',
                    'anchor': '',
                    'is_current': False,
                },
            ],
            'is_open': True,  # Dropdown contains current page
        },
    ],
    'current_page': <Page: Guides>,
    'request': <HttpRequest>,
}
```

### Multi-lingual Context (Spanish locale)

```python
{
    'menu_items': [
        {
            'type': 'page_link',
            'page': <Page: Acerca de>,  # Spanish translation
            'url': '/es/acerca-de/',
            'title': 'Acerca de',        # Uses Spanish page title
            'anchor': '',
            'is_current': False,
        },
        {
            'type': 'page_link',
            'page': <Page: Contact>,     # Falls back to English (no Spanish translation)
            'url': '/en/contact/',
            'title': 'Contact',
            'anchor': '',
            'is_current': False,
        },
    ],
    'current_page': <Page: Inicio>,
    'request': <HttpRequest>,  # request.LANGUAGE_CODE = 'es'
}
```

---

## Template Rendering Contract

### Desktop Navigation (≥1024px)

**Expected HTML Structure**:

```html
<nav aria-label="Main navigation">
  <ul class="menu menu-horizontal" role="menubar">
    <!-- Simple link -->
    <li role="none">
      <a href="/en/about/" role="menuitem">About Us</a>
    </li>

    <!-- Dropdown menu -->
    <li role="none">
      <button
        role="menuitem"
        aria-haspopup="true"
        aria-expanded="false"
        aria-controls="resources-submenu"
        class="dropdown-trigger"
      >
        Resources
      </button>

      <ul
        id="resources-submenu"
        role="menu"
        aria-labelledby="resources-trigger"
        class="dropdown-content"
        hidden
      >
        <li role="none">
          <a href="/en/guides/" role="menuitem" tabindex="-1">Guides</a>
        </li>
        <li role="none">
          <a href="/en/videos/" role="menuitem" tabindex="-1">Videos</a>
        </li>
      </ul>
    </li>
  </ul>
</nav>
```

**CSS Classes Required**:
- `menu menu-horizontal` - DaisyUI horizontal menu
- `dropdown-trigger` - Hover/click interaction trigger
- `dropdown-content` - Submenu styling
- Hidden attribute toggles visibility

---

### Mobile Navigation (<1024px)

**Expected HTML Structure** (DaisyUI drawer):

```html
<div class="drawer">
  <!-- Checkbox for state management -->
  <input id="nav-drawer" type="checkbox" class="drawer-toggle" />

  <!-- Main content -->
  <div class="drawer-content">
    <nav class="navbar bg-base-100" aria-label="Main navigation">
      <!-- Hamburger button -->
      <label
        for="nav-drawer"
        class="btn btn-square btn-ghost lg:hidden"
        aria-label="Open menu"
        aria-expanded="false"
        aria-controls="mobile-menu"
      >
        <svg><!-- Hamburger icon --></svg>
      </label>
    </nav>
  </div>

  <!-- Drawer side -->
  <div class="drawer-side">
    <label for="nav-drawer" class="drawer-overlay" aria-label="Close menu"></label>

    <aside id="mobile-menu" class="w-80 bg-base-200">
      <ul class="menu" role="menu">
        <!-- Simple link -->
        <li role="none">
          <a href="/en/about/" role="menuitem">About Us</a>
        </li>

        <!-- Accordion dropdown using <details> -->
        <li role="none">
          <details>
            <summary role="menuitem" aria-haspopup="true">
              Resources
              <span class="dropdown-icon" aria-hidden="true">▼</span>
            </summary>

            <ul role="menu" class="submenu">
              <li role="none">
                <a href="/en/guides/" role="menuitem">Guides</a>
              </li>
              <li role="none">
                <a href="/en/videos/" role="menuitem">Videos</a>
              </li>
            </ul>
          </details>
        </li>
      </ul>
    </aside>
  </div>
</div>
```

**CSS Classes Required**:
- `drawer`, `drawer-toggle`, `drawer-content`, `drawer-side` - DaisyUI drawer system
- `navbar bg-base-100` - Top navigation bar
- `btn btn-square btn-ghost` - Hamburger button styling
- `drawer-overlay` - Semi-transparent backdrop
- `w-80 bg-base-200` - Drawer width and background

---

## Accessibility Requirements

### ARIA Attributes

**All menu items MUST include**:

| Element                     | Required ARIA                                                               | Purpose                       |
| --------------------------- | --------------------------------------------------------------------------- | ----------------------------- |
| `<nav>`                     | `aria-label="Main navigation"`                                              | Landmark identification       |
| Top-level `<ul>`            | `role="menubar"` (desktop) or `role="menu"` (mobile)                        | Menu semantics                |
| Menu `<li>`                 | `role="none"`                                                               | Remove default list semantics |
| Link `<a>`                  | `role="menuitem"`                                                           | Menu item identification      |
| Dropdown trigger `<button>` | `role="menuitem"`, `aria-haspopup="true"`, `aria-expanded`, `aria-controls` | Dropdown state communication  |
| Submenu `<ul>`              | `role="menu"`, `aria-labelledby`                                            | Submenu context               |
| Current page link           | `aria-current="page"`                                                       | Current page indication       |
| Hamburger button            | `aria-label`, `aria-expanded`, `aria-controls`                              | Mobile menu control           |

### Keyboard Navigation

**Templates MUST support**:

| Key             | Action                             |
| --------------- | ---------------------------------- |
| Tab / Shift+Tab | Navigate between top-level items   |
| Enter / Space   | Activate links or toggle dropdowns |
| Escape          | Close open dropdowns               |
| Arrow Down / Up | Navigate within dropdowns          |

### Focus Management

**Required behavior**:
- All interactive elements must have visible focus indicator (3:1 contrast)
- Focus must not be trapped in dropdowns
- Skip link must be first focusable element
- Drawer opening should move focus to first menu item (progressive enhancement)

---

## Template Files

### Main Template

**File**: `src/navigation/templates/navigation/navigation.html`

**Responsibility**: Render complete navigation structure (desktop + mobile)

**Required template tags**:

```django
{% load navigation_tags %}
{% load i18n %}
```

**Expected includes**:

```django
{% if menu_items %}
  {% include 'navigation/desktop_menu.html' %}
  {% include 'navigation/mobile_menu.html' %}
{% endif %}
```

---

### Desktop Menu Template

**File**: `src/navigation/templates/navigation/desktop_menu.html`

**Renders**: Horizontal menubar for screens ≥1024px

**Loop structure**:

```django
{% for item in menu_items %}
  {% if item.type == 'page_link' or item.type == 'external_link' %}
    {% include 'navigation/menu_link.html' with item=item %}
  {% elif item.type == 'dropdown' %}
    {% include 'navigation/menu_dropdown.html' with dropdown=item %}
  {% endif %}
{% endfor %}
```

---

### Mobile Menu Template

**File**: `src/navigation/templates/navigation/mobile_menu.html`

**Renders**: Drawer with accordion dropdowns for screens <1024px

**Drawer structure**: DaisyUI drawer pattern with checkbox toggle

---

### Menu Link Component

**File**: `src/navigation/templates/navigation/menu_link.html`

**Props**:
- `item` (Dict) - MenuItem data structure
- `is_mobile` (Bool) - Render for mobile or desktop

**Renders**: Single `<a>` element with proper ARIA attributes

---

### Dropdown Component

**File**: `src/navigation/templates/navigation/menu_dropdown.html`

**Props**:
- `dropdown` (Dict) - Dropdown item data structure
- `is_mobile` (Bool) - Use `<details>` (mobile) or button+hover (desktop)

**Renders**: Dropdown trigger + submenu list

---

## Performance Contract

### Response Time

- **Menu rendering**: < 100ms for up to 50 items
- **Locale resolution**: < 50ms per page lookup
- **Template tag execution**: < 10ms overhead

### Database Queries

- **Optimal**: 1 query for menu settings + 1 query per unique page (with `select_related`)
- **Maximum acceptable**: N+1 queries (where N = number of menu items)
- **Caching**: Menu structure should be cached per site+locale combination

### Caching Strategy (Optional Enhancement)

```python
from django.core.cache import cache

def get_cached_menu(request):
    """Get menu from cache or render and cache it."""
    cache_key = f"nav_menu_{request.site.id}_{request.LANGUAGE_CODE}"
    menu = cache.get(cache_key)

    if menu is None:
        menu = render_navigation_menu(request)
        cache.set(cache_key, menu, timeout=3600)  # 1 hour

    return menu

# Invalidate cache on menu save
from django.db.models.signals import post_save
from navigation.models import NavigationMenuSetting

@receiver(post_save, sender=NavigationMenuSetting)
def invalidate_menu_cache(sender, instance, **kwargs):
    cache_pattern = f"nav_menu_{instance.site.id}_*"
    cache.delete_pattern(cache_pattern)
```

---

## Error Handling

### Missing Pages

**Scenario**: Page linked in menu is deleted or unpublished

**Behavior**: Template tag silently filters out missing pages

**Contract**: Templates receive only valid, publishable menu items

### Empty Menu

**Scenario**: No menu items configured in settings

**Behavior**: Template tag returns `{'menu_items': []}`

**Contract**: Templates check `{% if menu_items %}` and render nothing if empty

### Locale Fallback

**Scenario**: Page exists in default locale but not in current locale

**Behavior**: Link URL points to default locale version

**Contract**: Always returns a valid page (never None), fallback chain is default locale → skip item

### Broken External URLs

**Scenario**: External URL becomes invalid (404, domain expired)

**Behavior**: No validation performed, renders URL as-is

**Contract**: Administrator responsible for maintaining valid external links

---

## Versioning

### Current Version: 1.0.0

**Stability**: Stable - ready for implementation

**Breaking Changes**: None anticipated

**Future Enhancements**:
- Custom title translations (per-locale override text)
- Icon support for menu items
- Badge/count support (e.g., "News (3)")
- Multiple menu locations (footer, sidebar)

**Deprecation Policy**: 6-month notice before removing fields or changing contract

---

## Testing Contract

### Unit Tests

**Template tag tests** (`navigation/tests.py`):

```python
def test_navigation_menu_renders_page_links():
    """Template tag returns processed page link items."""
    # Setup: Create NavigationMenuSetting with page links
    # Assert: Returned context includes correctly formatted items

def test_navigation_menu_filters_deleted_pages():
    """Deleted pages are excluded from menu."""
    # Setup: Create menu with page link, delete the page
    # Assert: Template tag returns empty menu or skips deleted item

def test_navigation_menu_resolves_locale():
    """Page links resolve to current locale with fallback."""
    # Setup: Create menu, create Spanish translation for one page
    # Assert: Spanish page link, English fallback for untranslated

def test_dropdown_requires_at_least_one_child():
    """Empty dropdowns are filtered out."""
    # Setup: Create dropdown with child, delete the child page
    # Assert: Dropdown is removed from menu items
```

### Integration Tests

**Full rendering tests**:

```python
def test_navigation_renders_with_locale_switching():
    """Menu adapts when request locale changes."""
    # Setup: Create menu, create page translations
    # Assert: English request → English links, Spanish request → Spanish links

def test_navigation_marks_current_page():
    """Current page is marked with is_current=True."""
    # Setup: Create menu, make request to specific page
    # Assert: That page's menu item has is_current=True
```

### Accessibility Tests

**Automated WCAG testing** (using axe-core or similar):

```python
def test_navigation_passes_wcag_aa():
    """Rendered navigation has no accessibility violations."""
    # Setup: Render navigation template
    # Assert: axe scan returns 0 critical/serious violations

def test_keyboard_navigation_works():
    """All menu items are reachable via keyboard."""
    # Setup: Render menu, simulate Tab key presses
    # Assert: Can reach all links, can open/close dropdowns
```

---

## Summary

**API Surface**: 1 template tag (`{% navigation_menu %}`)

**Data Structures**: 3 item types (page_link, external_link, dropdown)

**Templates**: 5 files (navigation.html, desktop_menu.html, mobile_menu.html, menu_link.html, menu_dropdown.html)

**ARIA Requirements**: 10+ attributes for full WCAG 2.1 AA compliance

**Performance**: < 100ms rendering, caching recommended for high-traffic sites

**Stability**: Production-ready contract, versioned at 1.0.0
