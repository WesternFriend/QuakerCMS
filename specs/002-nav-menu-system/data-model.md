# Data Model: Multi-lingual Navigation Menu System

**Date**: 2025-10-26
**Status**: Complete

## Overview

This document defines the data model for the navigation menu system, including Django models, StreamField blocks, and database relationships.

## Entity Relationship

```text
NavigationMenuSetting (BaseSiteSetting)
  ├─ menu_items: StreamField
  │   ├─ TopLevelMenuBlock (StreamBlock)
  │   │   ├─ page_link: PageLinkBlock (StructBlock)
  │   │   │   ├─ page: FK → Page
  │   │   │   ├─ custom_title: CharField (optional)
  │   │   │   └─ anchor: CharField (optional)
  │   │   ├─ external_link: ExternalLinkBlock (StructBlock)
  │   │   │   ├─ url: URLField
  │   │   │   ├─ title: CharField
  │   │   │   └─ anchor: CharField (optional)
  │   │   └─ dropdown: DropdownMenuBlock (StructBlock)
  │   │       ├─ title: CharField
  │   │       └─ items: MenuItemBlock (StreamBlock)
  │   │           ├─ page_link: PageLinkBlock
  │   │           └─ external_link: ExternalLinkBlock
  │   └─ (max 2 levels - no nested dropdowns)
  └─ site: FK → Site (inherited from BaseSiteSetting)

Page (Wagtail core model)
  ├─ locale: FK → Locale
  ├─ translation_key: UUID (groups translations)
  └─ localized: Manager for translations

Locale (Wagtail core model)
  └─ language_code: CharField (en, es, fr, etc.)
```

## Models

### NavigationMenuSetting

**Purpose**: Site-wide navigation menu configuration accessible via Wagtail Settings admin.

**File**: `src/navigation/models.py`

```python
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel

@register_setting
class NavigationMenuSetting(BaseSiteSetting):
    """
    Site-wide navigation menu configuration.
    Accessible via Settings → Navigation Menu in Wagtail admin.
    """
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

**Fields**:

| Field        | Type        | Required | Description                                      |
| ------------ | ----------- | -------- | ------------------------------------------------ |
| `menu_items` | StreamField | No       | Top-level menu items (links and dropdowns)       |
| `site`       | ForeignKey  | Yes      | Associated site (inherited from BaseSiteSetting) |

**Relationships**:
- **Many-to-One** with `Site` (inherited from `BaseSiteSetting`)
- **References** `Page` objects through StreamField blocks

**Validation Rules**:
- Maximum 2 levels of nesting (enforced by block structure - MenuItemBlock cannot contain DropdownMenuBlock)
- No broken page references (handled by template rendering - deleted pages filtered out)
- Valid URL format for external links (handled by URLBlock validation)

**State Transitions**: None (simple CRUD model)

---

## StreamField Blocks

### TopLevelMenuBlock

**Purpose**: Container for top-level navigation items (can include links OR dropdowns).

**File**: `src/navigation/blocks.py`

```python
from wagtail.blocks import StreamBlock

class TopLevelMenuBlock(StreamBlock):
    """
    Top-level menu items.
    Can contain simple links (pages/URLs) or dropdown menus.
    """
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    dropdown = DropdownMenuBlock()

    class Meta:
        icon = 'list-ul'
        label = 'Navigation Menu'
        max_num = 10  # Reasonable limit for usability
```

**Allowed Child Types**:
- `page_link` (PageLinkBlock)
- `external_link` (ExternalLinkBlock)
- `dropdown` (DropdownMenuBlock)

**Constraints**:
- Maximum 10 top-level items (configurable via `max_num`)
- Cannot contain nested `TopLevelMenuBlock` instances

---

### PageLinkBlock

**Purpose**: Link to an internal Wagtail page with optional custom title.

**File**: `src/navigation/blocks.py`

```python
from wagtail.blocks import StructBlock, CharBlock, PageChooserBlock

class PageLinkBlock(StructBlock):
    """
    Internal page link.
    Optionally override the page title with a custom menu label.
    """
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
        template = 'navigation/blocks/page_link.html'
```

**Fields**:

| Field          | Type             | Required | Max Length | Description                              |
| -------------- | ---------------- | -------- | ---------- | ---------------------------------------- |
| `page`         | PageChooserBlock | Yes      | -          | Target Wagtail page                      |
| `custom_title` | CharBlock        | No       | 100        | Custom menu label (overrides page title) |
| `anchor`       | CharBlock        | No       | 50         | Fragment identifier (without #)          |

**Behavior**:
- If `custom_title` is blank, use `page.title` from the linked page
- If `anchor` is provided, append `#{anchor}` to URL
- At render time, resolve to locale-specific page translation

---

### ExternalLinkBlock

**Purpose**: Link to an external URL (outside the Wagtail site).

**File**: `src/navigation/blocks.py`

```python
from wagtail.blocks import StructBlock, CharBlock, URLBlock

class ExternalLinkBlock(StructBlock):
    """
    External URL link.
    Use for links to external websites or non-Wagtail pages.
    """
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
        template = 'navigation/blocks/external_link.html'
```

**Fields**:

| Field    | Type      | Required | Max Length | Description                             |
| -------- | --------- | -------- | ---------- | --------------------------------------- |
| `url`    | URLBlock  | Yes      | -          | External URL (validated for http/https) |
| `title`  | CharBlock | Yes      | 100        | Menu link text                          |
| `anchor` | CharBlock | No       | 50         | Fragment identifier (without #)         |

**Validation**:
- URL must start with `http://` or `https://` (URLBlock validation)
- Title cannot be empty

**Behavior**:
- If `anchor` is provided, append `#{anchor}` to URL
- No locale translation (external URLs are static)

---

### DropdownMenuBlock

**Purpose**: Collapsible menu containing multiple child links (max 1 level of nesting).

**File**: `src/navigation/blocks.py`

```python
from wagtail.blocks import StructBlock, CharBlock

class DropdownMenuBlock(StructBlock):
    """
    Dropdown menu with child items.
    Can contain page links and external links (NO nested dropdowns).
    """
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
        template = 'navigation/blocks/dropdown.html'
```

**Fields**:

| Field   | Type          | Required | Description                            |
| ------- | ------------- | -------- | -------------------------------------- |
| `title` | CharBlock     | Yes      | Dropdown label (non-clickable trigger) |
| `items` | MenuItemBlock | Yes      | Child menu items (StreamBlock)         |

**Constraints**:
- Must have at least one child item
- Cannot contain other `DropdownMenuBlock` instances (enforced by `MenuItemBlock` definition)

**Behavior**:
- On desktop: Opens on hover, stays open on click
- On mobile: Opens on click within hamburger drawer (accordion-style)
- Title itself is not a link (non-navigable)

---

### MenuItemBlock

**Purpose**: Container for items within a dropdown (ONLY simple links, no nesting).

**File**: `src/navigation/blocks.py`

```python
from wagtail.blocks import StreamBlock

class MenuItemBlock(StreamBlock):
    """
    Items that can appear within a dropdown menu.
    Only simple links allowed - NO nested dropdowns.
    """
    page_link = PageLinkBlock()
    external_link = ExternalLinkBlock()
    # NOTE: Dropdown menu type is intentionally excluded to prevent 3+ level nesting

    class Meta:
        icon = 'link'
        label = 'Menu Item'
        max_num = 20  # Reasonable limit per dropdown
```

**Allowed Child Types**:
- `page_link` (PageLinkBlock)
- `external_link` (ExternalLinkBlock)

**Constraints**:
- Maximum 20 items per dropdown
- **Cannot contain `dropdown`** - this enforces 2-level maximum

---

## Database Schema

### Django Migration

**File**: `src/navigation/migrations/0001_initial.py` (auto-generated)

```python
from django.db import migrations
import wagtail.fields
import wagtail.blocks
import wagtail.contrib.settings.models

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('wagtailcore', '__latest__'),  # Depends on Wagtail core
    ]

    operations = [
        migrations.CreateModel(
            name='NavigationMenuSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menu_items', wagtail.fields.StreamField(
                    [
                        ('page_link', wagtail.blocks.StructBlock([...])),
                        ('external_link', wagtail.blocks.StructBlock([...])),
                        ('dropdown', wagtail.blocks.StructBlock([...])),
                    ],
                    blank=True,
                    use_json_field=True,
                )),
                ('site', models.OneToOneField(
                    editable=False,
                    on_delete=models.CASCADE,
                    to='wagtailcore.site'
                )),
            ],
            options={
                'verbose_name': 'Navigation Menu',
                'verbose_name_plural': 'Navigation Menu',
            },
            bases=(wagtail.contrib.settings.models.BaseSiteSetting, models.Model),
        ),
    ]
```

### Storage Format

**Table**: `navigation_navigationmenusetting`

| Column       | Type    | Constraints         | Description              |
| ------------ | ------- | ------------------- | ------------------------ |
| `id`         | INTEGER | PRIMARY KEY         | Auto-increment ID        |
| `site_id`    | INTEGER | FOREIGN KEY, UNIQUE | Reference to Site table  |
| `menu_items` | JSON    | NOT NULL            | StreamField data as JSON |

**JSON Structure Example**:

```json
[
  {
    "type": "page_link",
    "value": {
      "page": 3,
      "custom_title": "",
      "anchor": ""
    },
    "id": "abc123"
  },
  {
    "type": "dropdown",
    "value": {
      "title": "Resources",
      "items": [
        {
          "type": "page_link",
          "value": {
            "page": 5,
            "custom_title": "User Guides",
            "anchor": ""
          },
          "id": "def456"
        },
        {
          "type": "external_link",
          "value": {
            "url": "https://example.com/docs",
            "title": "Documentation",
            "anchor": ""
          },
          "id": "ghi789"
        }
      ]
    },
    "id": "jkl012"
  }
]
```

---

## Query Patterns

### Get Navigation Menu for Current Request

```python
from navigation.models import NavigationMenuSetting

# In view or template tag
menu_settings = NavigationMenuSetting.for_request(request)
menu_items = menu_settings.menu_items if menu_settings else []
```

### Get Locale-Specific Page for Menu Item

```python
from wagtail.models import Locale, Page

def get_localized_page(page, locale_code):
    """
    Get page translation for given locale, falling back to default.
    """
    try:
        target_locale = Locale.objects.get(language_code=locale_code)
        return page.localized.get(locale=target_locale)
    except (Locale.DoesNotExist, Page.DoesNotExist):
        # Fall back to default locale
        default_locale = Locale.get_default()
        try:
            return page.localized.get(locale=default_locale)
        except Page.DoesNotExist:
            return None  # Page deleted in all locales
```

### Check if Page is Used in Navigation

```python
def is_page_in_navigation(page):
    """
    Check if a page is referenced in any navigation menu.
    Useful for preventing deletion or showing warnings.

    ⚠️ PERFORMANCE NOTE: This reference implementation iterates through all
    menu items in Python. For production use with large sites or frequent calls,
    consider the optimized alternatives below.
    """
    from navigation.models import NavigationMenuSetting

    for setting in NavigationMenuSetting.objects.all():
        for item in setting.menu_items:
            if item.block_type == 'page_link':
                if item.value.get('page') == page:
                    return True
            elif item.block_type == 'dropdown':
                for child in item.value.get('items', []):
                    if child.block_type == 'page_link':
                        if child.value.get('page') == page:
                            return True
    return False
```

**Optimized Alternatives for Production**:

```python
# Option 1: Database-level query with JSONField lookups (Django 3.1+)
from django.db.models import Q
from navigation.models import NavigationMenuSetting

def is_page_in_navigation_optimized(page):
    """
    Check if page is in navigation using efficient database queries.
    Works with PostgreSQL JSONField backend.
    """
    # Check for page_link blocks at top level or within dropdowns
    return NavigationMenuSetting.objects.filter(
        Q(menu_items__contains=[{"type": "page_link", "value": {"page": page.pk}}]) |
        Q(menu_items__contains=[{"type": "dropdown", "value": {"items": [{"type": "page_link", "value": {"page": page.pk}}]}}])
    ).exists()

# Option 2: Caching strategy for frequently accessed menus
from django.core.cache import cache
from django.views.decorators.cache import cache_page

def get_navigation_for_request_cached(request):
    """
    Get navigation menu with caching to reduce database queries.
    Cache key should invalidate when menu settings change.
    """
    cache_key = f"navigation_menu_{request.site.pk}_{request.LANGUAGE_CODE}"
    menu_settings = cache.get(cache_key)

    if menu_settings is None:
        menu_settings = NavigationMenuSetting.for_request(request)
        # Cache for 1 hour; invalidate in NavigationMenuSetting.save()
        cache.set(cache_key, menu_settings, 60 * 60)

    return menu_settings

# Option 3: Signal-based cache invalidation
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from navigation.models import NavigationMenuSetting

@receiver([post_save, post_delete], sender=NavigationMenuSetting)
def invalidate_navigation_cache(sender, instance, **kwargs):
    """Clear navigation cache when settings change."""
    cache_pattern = f"navigation_menu_{instance.site.pk}_*"
    cache.delete_pattern(cache_pattern)  # Requires Redis backend
```

---

## Data Volume Estimates

### Typical Site

- **Top-level items**: 5-8
- **Dropdowns**: 2-3
- **Items per dropdown**: 3-7
- **Total menu items**: 15-30
- **JSON size**: ~2-5 KB per menu

### Large Site

- **Top-level items**: 10 (maximum recommended)
- **Dropdowns**: 5
- **Items per dropdown**: 10-15
- **Total menu items**: 40-85
- **JSON size**: ~8-15 KB per menu

### Performance Considerations

- **Database queries**: 1 query for menu + N queries for page translations
- **Caching strategy**: Menu structure rarely changes, good candidate for caching
- **Rendering time**: < 100ms for 50 items (spec requirement)

---

## Migration Path

### Adding Navigation to Existing Site

1. Run migration: `python manage.py migrate navigation`
2. Add `'navigation'` to `INSTALLED_APPS` in settings
3. Access Settings → Navigation Menu in admin
4. Create menu items
5. Include `{% load navigation_tags %}{% navigation_menu %}` in base template

### Updating Menu Structure

When changing block structure (e.g., adding new fields):

1. Modify block definitions in `blocks.py`
2. Generate migration: `python manage.py makemigrations navigation`
3. Review migration for data transformations
4. Run migration: `python manage.py migrate navigation`
5. Update templates if field names changed

### Rollback Considerations

- StreamField changes are typically additive (new optional fields)
- Removing required fields requires data migration to set defaults
- Always test migrations on staging before production

---

## Summary

**Core Models**: 1 (`NavigationMenuSetting`)
**StreamField Blocks**: 5 (TopLevelMenuBlock, PageLinkBlock, ExternalLinkBlock, DropdownMenuBlock, MenuItemBlock)
**Database Tables**: 1 (`navigation_navigationmenusetting`)
**Relationships**: Site → NavigationMenuSetting (One-to-One), NavigationMenuSetting → Pages (Many-to-Many via JSON)

**Key Design Decisions**:
- StreamField provides flexible, validated structure
- Separate block types enforce 2-level nesting limit
- Locale resolution happens at render time (dynamic)
- Single menu per site (simplicity over flexibility)

**Next Steps**: Define template contracts and API surface in `contracts/` directory.
