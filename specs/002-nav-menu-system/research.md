# Research: Multi-lingual Navigation Menu System

**Date**: 2025-10-26
**Status**: Complete

## Overview

This document consolidates research findings for implementing a Wagtail-based navigation menu system with multi-lingual support, WCAG 2.1 AA compliance, and DaisyUI responsive design.

## 1. Wagtail StreamField for Navigation Menus

### Decision

Use Wagtail's `StreamField` with custom `StructBlock` components for menu items, stored in a `BaseSiteSetting` model.

### Rationale

- **Native Wagtail pattern**: StreamField is the recommended way to build flexible, structured content in Wagtail
- **Admin UX**: Provides drag-and-drop reordering, collapsible panels, and inline editing
- **Validation**: Built-in validation framework for enforcing nesting limits
- **Type safety**: Each block type (PageLink, ExternalLink, Dropdown) has clearly defined fields
- **Migration-friendly**: StreamField changes generate automatic Django migrations

### Implementation Pattern

```python
# navigation/blocks.py
from wagtail.blocks import StructBlock, CharBlock, URLBlock, StreamBlock, PageChooserBlock
from wagtail.fields import StreamField

class PageLinkBlock(StructBlock):
    page = PageChooserBlock(required=True)
    custom_title = CharBlock(required=False, help_text="Override page title")
    anchor = CharBlock(required=False, help_text="Optional #anchor")

    class Meta:
        icon = 'doc-full'
        label = 'Page Link'

class ExternalLinkBlock(StructBlock):
    url = URLBlock(required=True)
    title = CharBlock(required=True)
    anchor = CharBlock(required=False)

    class Meta:
        icon = 'link'
        label = 'External Link'

class MenuItemBlock(StreamBlock):
    """Child items for dropdowns - only simple links allowed"""
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()

    class Meta:
        max_num = 20  # Reasonable limit per dropdown

class DropdownMenuBlock(StructBlock):
    title = CharBlock(required=True, help_text="Dropdown menu label")
    items = MenuItemBlock(required=True)

    class Meta:
        icon = 'list-ul'
        label = 'Dropdown Menu'

class TopLevelMenuBlock(StreamBlock):
    """Top-level menu items - can be links OR dropdowns"""
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    dropdown = DropdownMenuBlock()

    class Meta:
        max_num = 10  # Reasonable limit for top-level items

# navigation/models.py
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField

@register_setting
class NavigationMenuSetting(BaseSiteSetting):
    menu_items = StreamField(
        TopLevelMenuBlock(),
        blank=True,
        use_json_field=True,
        help_text="Define the site navigation menu"
    )

    panels = [
        FieldPanel('menu_items'),
    ]
```

### Alternatives Considered

1. **FlatMenu approach (django-wagtailmenus)**: Third-party package
   - Rejected: Adds dependency, more complex than needed for single menu
   - Our use case is simpler - single menu, clear structure

2. **JSONField with custom admin widget**: Manual JSON structure
   - Rejected: Loses Wagtail admin UX benefits, no validation, harder to maintain
   - StreamField provides superior editing experience

3. **Separate Menu and MenuItem models with ForeignKey**: Traditional Django approach
   - Rejected: More database queries, harder to reorder, StreamField is Wagtail-native pattern
   - StreamField stores structure efficiently in single column

### Key Technical Notes

- **Nesting enforcement**: StreamBlock doesn't support nested StreamBlocks by default - our design prevents this by using different block types (TopLevelMenuBlock vs MenuItemBlock)
- **Performance**: StreamField data is stored as JSON, single database query retrieves entire menu
- **Translations**: Custom title translations handled via separate mechanism (see Multi-lingual section)

---

## 2. DaisyUI Drawer Component

### Decision

Use DaisyUI's native `drawer` component for mobile hamburger menu, implementing the left-side slide-in pattern.

### Rationale

- **Zero JavaScript required**: Uses CSS-only `:checked` pseudo-class with checkbox hack
- **Accessibility built-in**: Proper focus management when using with Alpine.js enhancement
- **Theme-aware**: Automatically adapts to light/dark theme via DaisyUI theme system
- **Responsive**: Works across all viewport sizes without media query management
- **Tailwind-native**: Integrates seamlessly with existing django-tailwind setup

### Implementation Pattern

```html
<!-- core/templates/components/navigation.html -->
<div class="drawer lg:drawer-open">
  <!-- Checkbox for drawer state (mobile only) -->
  <input id="nav-drawer" type="checkbox" class="drawer-toggle" />

  <!-- Main content area -->
  <div class="drawer-content">
    <!-- Navbar for desktop, hamburger for mobile -->
    <nav class="navbar bg-base-100" aria-label="Main navigation">
      <!-- Mobile: Hamburger button -->
      <div class="lg:hidden">
        <label for="nav-drawer" class="btn btn-square btn-ghost" aria-label="Open menu">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </label>
      </div>

      <!-- Desktop: Horizontal menu -->
      <div class="hidden lg:flex lg:flex-1">
        <ul class="menu menu-horizontal" role="menubar">
          <!-- Menu items rendered here -->
        </ul>
      </div>
    </nav>

    <!-- Page content goes here -->
    <main id="main-content">
      {% block content %}{% endblock %}
    </main>
  </div>

  <!-- Drawer side (mobile only) -->
  <div class="drawer-side lg:hidden">
    <!-- Overlay backdrop -->
    <label for="nav-drawer" class="drawer-overlay" aria-label="Close menu"></label>

    <!-- Drawer content -->
    <aside class="w-80 min-h-full bg-base-200">
      <!-- Close button -->
      <div class="flex justify-end p-4">
        <label for="nav-drawer" class="btn btn-sm btn-circle btn-ghost" aria-label="Close menu">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </label>
      </div>

      <!-- Mobile menu items -->
      <ul class="menu p-4 w-full" role="menu">
        <!-- Accordion-style dropdowns here -->
      </ul>
    </aside>
  </div>
</div>
```

### Accessibility Enhancements

```html
<!-- Enhanced with Alpine.js for better a11y -->
<div x-data="{ drawerOpen: false }" class="drawer">
  <input
    id="nav-drawer"
    type="checkbox"
    class="drawer-toggle"
    x-model="drawerOpen"
    @change="$nextTick(() => drawerOpen && $refs.firstItem.focus())"
  />

  <div class="drawer-content">
    <label
      for="nav-drawer"
      class="btn btn-square btn-ghost"
      :aria-expanded="drawerOpen"
      aria-controls="mobile-menu"
    >
      <!-- Hamburger icon -->
    </label>
  </div>

  <div class="drawer-side">
    <label for="nav-drawer" class="drawer-overlay"></label>
    <aside id="mobile-menu" class="w-80 bg-base-200">
      <ul class="menu" role="menu">
        <li><a x-ref="firstItem" href="#">First Item</a></li>
        <!-- More items -->
      </ul>
    </aside>
  </div>
</div>
```

### Alternatives Considered

1. **Full-screen modal overlay**: Cover entire viewport
   - Rejected: Less intuitive for users expecting side drawer pattern
   - Drawer is modern mobile UX standard

2. **Simple dropdown below hamburger**: Pushes content down
   - Rejected: Awkward on long menus, breaks page layout
   - Doesn't work well with nested menus

3. **Right-side drawer**: Slide from right edge
   - Rejected: Left-side is more common in LTR languages
   - User expectation is left-side for primary navigation

### Key Technical Notes

- **CSS-only fallback**: Works without JavaScript using `:checked` selector
- **Progressive enhancement**: Alpine.js adds focus management and smooth UX
- **Breakpoint**: `lg:` breakpoint (1024px) switches between mobile/desktop modes
- **Theme variables**: Uses `bg-base-100`, `bg-base-200` for automatic theme support

---

## 3. WCAG 2.1 AA Navigation Patterns

### Decision

Implement ARIA menubar pattern for desktop, ARIA menu pattern for mobile, with full keyboard navigation support.

### Rationale

- **Legal compliance**: WCAG 2.1 AA is required for government sites and increasingly for all public sites
- **Screen reader support**: Proper ARIA roles ensure navigation is announced correctly
- **Keyboard accessibility**: 15-20% of users rely on keyboard navigation (disabilities, power users, mobile)
- **Best practices**: Following W3C WAI-ARIA Authoring Practices Guide patterns

### Implementation Pattern

**Desktop Horizontal Menu** (ARIA menubar):

```html
<nav aria-label="Main navigation">
  <ul class="menu menu-horizontal" role="menubar">
    <!-- Simple link item -->
    <li role="none">
      <a href="/about" role="menuitem">About</a>
    </li>

    <!-- Dropdown menu item -->
    <li role="none">
      <button
        role="menuitem"
        aria-haspopup="true"
        aria-expanded="false"
        aria-controls="resources-submenu"
        @click="toggleDropdown('resources')"
        @keydown.enter.prevent="toggleDropdown('resources')"
        @keydown.space.prevent="toggleDropdown('resources')"
        @keydown.escape="closeDropdown('resources')"
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
          <a href="/resources/guides" role="menuitem" tabindex="-1">Guides</a>
        </li>
        <li role="none">
          <a href="/resources/videos" role="menuitem" tabindex="-1">Videos</a>
        </li>
      </ul>
    </li>
  </ul>
</nav>
```

**Mobile Accordion Menu**:

```html
<ul class="menu" role="menu">
  <!-- Accordion item using <details> for progressive enhancement -->
  <li role="none">
    <details>
      <summary role="menuitem" aria-haspopup="true">
        Resources
        <span class="dropdown-icon" aria-hidden="true">▼</span>
      </summary>

      <ul role="menu" class="submenu">
        <li role="none">
          <a href="/resources/guides" role="menuitem">Guides</a>
        </li>
        <li role="none">
          <a href="/resources/videos" role="menuitem">Videos</a>
        </li>
      </ul>
    </details>
  </li>
</ul>
```

**Skip Link** (WCAG 2.4.1 Bypass Blocks):

```html
<!-- First element in <body> -->
<a href="#main-content" class="skip-link sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:p-4 focus:bg-primary focus:text-primary-content">
  Skip to main content
</a>

<!-- Later in page -->
<main id="main-content" tabindex="-1">
  <!-- Page content -->
</main>
```

**Current Page Indication**:

```html
<li role="none">
  <a
    href="/about"
    role="menuitem"
    aria-current="page"
    class="active"
  >
    About
  </a>
</li>
```

### Keyboard Navigation Requirements

| Key           | Context          | Action                                          |
| ------------- | ---------------- | ----------------------------------------------- |
| Tab           | Anywhere         | Move to next top-level menu item or out of menu |
| Shift+Tab     | Anywhere         | Move to previous top-level item or out of menu  |
| Enter / Space | Dropdown trigger | Toggle submenu open/closed                      |
| Enter / Space | Link item        | Activate link (navigate to page)                |
| Escape        | Open dropdown    | Close dropdown, return focus to trigger         |
| Arrow Down    | Dropdown trigger | Open dropdown, focus first item                 |
| Arrow Up      | Dropdown trigger | Open dropdown, focus last item                  |
| Arrow Down    | Within dropdown  | Focus next item (wrap to first)                 |
| Arrow Up      | Within dropdown  | Focus previous item (wrap to last)              |

### Focus Indicators

```css
/* Ensure visible focus for keyboard users */
.menu a:focus,
.menu button:focus {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}

/* High contrast for dark/light themes */
@media (prefers-color-scheme: dark) {
  .menu a:focus,
  .menu button:focus {
    outline-color: #60a5fa; /* Bright blue */
  }
}
```

### Color Contrast Requirements

- **Normal text**: 4.5:1 contrast ratio minimum
- **Large text** (18pt+): 3:1 contrast ratio minimum
- **Interactive components**: 3:1 contrast ratio for boundaries/states
- **Focus indicators**: 3:1 contrast against adjacent colors

### Alternatives Considered

1. **Pure `<nav>` with `<a>` links**: No ARIA roles
   - Rejected: Doesn't communicate dropdown structure to screen readers
   - Users don't know which items have submenus

2. **ARIA tree pattern**: File/folder tree structure
   - Rejected: Overly complex for navigation, not standard pattern
   - Menubar is the recommended pattern for horizontal navigation

3. **Disclosure widget pattern**: Simple show/hide
   - Rejected: Doesn't convey navigation semantics
   - Menu pattern better communicates purpose

### Key Technical Notes

- **Progressive enhancement**: `<details>` element works without JavaScript
- **ARIA overrides**: `role="none"` removes default list semantics for menu pattern
- **Focus management**: Dropdown items use `tabindex="-1"` until dropdown opens
- **Mobile vs desktop**: Different ARIA patterns appropriate for different layouts
- **Testing tools**: axe DevTools, WAVE, NVDA/JAWS screen readers

---

## 4. Multi-lingual Menu Rendering in Wagtail

### Decision

Query page translations at render time using Wagtail's `Page.localized` and locale context, with fallback to default locale for untranslated pages.

### Rationale

- **Dynamic rendering**: Menu adapts to current request locale without storing duplicate menu structures
- **Single source of truth**: Menu defined once in default locale, translations pulled from page relationships
- **Automatic updates**: When page translations are added/removed, menu automatically reflects changes
- **Fallback strategy**: Graceful degradation for partially translated sites

### Implementation Pattern

**Template Tag for Locale-Aware Menu Rendering**:

```python
# navigation/templatetags/navigation_tags.py
from django import template
from django.utils.translation import get_language
from wagtail.models import Locale, Page

register = template.Library()

@register.inclusion_tag('navigation/navigation.html', takes_context=True)
def navigation_menu(context):
    """Render navigation menu with locale-aware page links"""
    request = context['request']
    current_locale = Locale.get_active()
    default_locale = Locale.get_default()

    # Get menu settings
    from navigation.models import NavigationMenuSetting
    menu_settings = NavigationMenuSetting.for_request(request)

    if not menu_settings.menu_items:
        return {'menu_items': []}

    # Process menu items to get locale-specific pages
    processed_items = []
    for item in menu_settings.menu_items:
        processed_item = process_menu_item(item, current_locale, default_locale)
        if processed_item:  # Skip items with deleted pages
            processed_items.append(processed_item)

    return {
        'menu_items': processed_items,
        'current_page': context.get('page'),
        'request': request,
    }

def process_menu_item(item, current_locale, default_locale):
    """Convert menu item to locale-specific version"""
    item_type = item.block_type

    if item_type == 'page_link':
        page = item.value['page']

        # Skip deleted pages
        if not page or not page.live:
            return None

        # Try to get page translation in current locale
        try:
            localized_page = page.localized.get(locale=current_locale)
        except Page.DoesNotExist:
            # Fall back to default locale version
            try:
                localized_page = page.localized.get(locale=default_locale)
            except Page.DoesNotExist:
                # Page doesn't exist in default locale either - skip
                return None

        return {
            'type': 'page_link',
            'page': localized_page,
            'url': localized_page.url,
            'title': item.value.get('custom_title') or localized_page.title,
            'anchor': item.value.get('anchor', ''),
        }

    elif item_type == 'external_link':
        return {
            'type': 'external_link',
            'url': item.value['url'] + (item.value.get('anchor', '') or ''),
            'title': item.value['title'],
        }

    elif item_type == 'dropdown':
        child_items = []
        for child in item.value['items']:
            processed_child = process_menu_item(child, current_locale, default_locale)
            if processed_child:
                child_items.append(processed_child)

        # Only include dropdown if it has at least one valid child
        if child_items:
            return {
                'type': 'dropdown',
                'title': item.value['title'],
                'items': child_items,
            }

    return None
```

**Template Usage**:

```django
{# base.html #}
{% load navigation_tags %}

<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
  <!-- head content -->
</head>
<body>
  {% navigation_menu %}

  <main id="main-content">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

**Custom Title Translations** (Future Enhancement):

```python
# If custom titles need per-locale translations, extend the block:
class TranslatableCharBlock(StructBlock):
    default_text = CharBlock(required=True, help_text="Default text")
    translations = StreamBlock([
        ('translation', StructBlock([
            ('locale', ChoiceBlock(choices=get_locale_choices)),
            ('text', CharBlock()),
        ]))
    ], required=False)

    def get_text_for_locale(self, locale_code):
        for translation in self.value.get('translations', []):
            if translation.value['locale'] == locale_code:
                return translation.value['text']
        return self.value['default_text']
```

### Wagtail Locale API

Key methods for locale-aware queries:

```python
# Get current active locale
current_locale = Locale.get_active()

# Get default locale
default_locale = Locale.get_default()

# Get specific page translation
translated_page = page.get_translation(locale)

# Get translation or return None
try:
    translated_page = page.localized.get(locale=locale)
except Page.DoesNotExist:
    translated_page = None

# Get all translations of a page
all_translations = page.get_translations(inclusive=True)  # includes self

# Check if page has translation
has_spanish = page.get_translations().filter(locale__language_code='es').exists()
```

### Alternatives Considered

1. **Separate menu per locale**: Store complete menu structure for each language
   - Rejected: Massive duplication, nightmare to maintain
   - Menu structure changes would require updating N locales

2. **Pre-generate locale menus in signal**: Cache menu on page save
   - Rejected: Complex cache invalidation, not worth the optimization
   - Single menu query per request is acceptable performance

3. **Client-side locale switching**: JavaScript swaps links
   - Rejected: Doesn't work without JS, SEO issues
   - Server-side rendering is more reliable

### Key Technical Notes

- **Locale context**: Wagtail automatically sets active locale per request based on URL prefix
- **Translation sync**: Menu automatically reflects when pages are published/unpublished in locales
- **Deleted pages**: Template tag filters out deleted/unpublished pages automatically
- **Performance**: Single database query for menu + N queries for page translations (acceptable for <50 items)
- **Caching**: Can add `cache_result` decorator if needed, invalidate on page publish signal

---

## 5. StreamField Nesting Limits (2-Level Maximum)

### Decision

Use separate `StreamBlock` types with different allowed children to enforce 2-level maximum at the schema level.

### Rationale

- **Prevent at source**: Impossible to create 3+ level nesting in admin interface
- **Clear UX**: Admin sees only valid block types for each context
- **No runtime validation**: Structural constraint prevents invalid data from existing
- **Type safety**: Python typing clearly distinguishes top-level vs child item blocks

### Implementation Pattern

```python
# navigation/blocks.py
from wagtail.blocks import StreamBlock, StructBlock

# Level 2: Child items (leaves only - no more nesting allowed)
class MenuItemBlock(StreamBlock):
    """Items that can appear within a dropdown - ONLY simple links"""
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    # NOTE: NO DropdownMenuBlock here - prevents 3rd level nesting

    class Meta:
        icon = 'list-ul'
        label = 'Menu Items'
        max_num = 20

# Level 1: Top-level items (can contain dropdowns OR be simple links)
class TopLevelMenuBlock(StreamBlock):
    """Items that can appear at top level of navigation"""
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    dropdown = DropdownMenuBlock()  # Contains MenuItemBlock children

    class Meta:
        icon = 'list-ul'
        label = 'Navigation Menu'
        max_num = 10
```

### Admin Interface Behavior

When editing the navigation menu:

1. **At top level**: Admin sees three block types to add
   - Page Link
   - External Link
   - Dropdown Menu

2. **Inside a dropdown**: Admin sees only two block types to add
   - Page Link
   - External Link
   - (Dropdown Menu option is NOT available)

This makes it impossible to create:
```
Dropdown
  └─ Dropdown  ❌ Cannot add this
       └─ Page Link
```

### Validation (Defense in Depth)

The block structure prevents invalid nesting at the schema level - no runtime validation needed:

```python
# MenuItemBlock (used inside dropdowns) ONLY allows:
class MenuItemBlock(StreamBlock):
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    # DropdownMenuBlock is NOT included here
```

This makes it structurally impossible to create nested dropdowns. The admin interface will not show the "Dropdown Menu" option when adding items inside a dropdown.

### Alternatives Considered

1. **Runtime validation on save**: Check nesting depth in `clean()` method
   - Still implemented as defense-in-depth, but not primary mechanism
   - Better to prevent at structural level

2. **JavaScript validation in admin**: Client-side check
   - Rejected: Can be bypassed, not reliable
   - Server-side structure is source of truth

3. **Custom StreamBlock with depth tracking**: Complex custom implementation
   - Rejected: Over-engineered, simple type separation is cleaner
   - Wagtail's block system already provides what we need

4. **Single StreamBlock with conditional logic**: Check parent context
   - Rejected: More complex, error-prone
   - Separate block types are more explicit and type-safe

### User Experience

Admin user tries to add dropdown inside dropdown:

1. Clicks "Add menu item" inside a dropdown
2. Sees modal with options: "Page Link" and "External Link" only
3. "Dropdown Menu" option is not present
4. User cannot create invalid structure

### Key Technical Notes

- **Type system**: Python type checkers understand the nesting constraints
- **Database storage**: Still JSON, but schema is enforced at application level
- **Migration safety**: Changing block structure requires migration
- **Admin customization**: Can add help text explaining the 2-level limit

---

## Summary of Decisions

| Area           | Decision                      | Key Benefit                                  |
| -------------- | ----------------------------- | -------------------------------------------- |
| Data Structure | StreamField with StructBlocks | Native Wagtail pattern, great admin UX       |
| Mobile Menu    | DaisyUI drawer (left-side)    | Accessible, theme-aware, zero-JS option      |
| Accessibility  | ARIA menubar + menu patterns  | WCAG 2.1 AA compliant, screen reader support |
| Multi-lingual  | Runtime query with fallback   | Single source of truth, automatic updates    |
| Nesting Limit  | Separate StreamBlock types    | Impossible to create invalid structure       |

## Next Steps

1. **Phase 1**: Create data model based on StreamField structure
2. **Phase 1**: Define template contracts (context variables, structure)
3. **Phase 1**: Generate quickstart guide for developers
4. **Phase 2**: Break down into implementation tasks

---

**Research Status**: ✅ **Complete** - All technical unknowns resolved. Ready for Phase 1 design.
