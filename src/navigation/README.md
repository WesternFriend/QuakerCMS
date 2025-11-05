# Navigation App

Provides a site-wide navigation menu system for QuakerCMS with support for:
- Page links (to Wagtail pages)
- External links
- Dropdown menus (single level)
- Mobile-responsive drawer navigation
- WCAG 2.1 AA accessibility compliance

## Quick Start

### Scaffold Test Content

To quickly set up test pages and navigation menu for development:

```bash
cd src
python manage.py scaffold_navbar_content
```

This creates:
- **About** page (top-level)
- **Programs** page with dropdown containing:
  - Programs overview
  - Adult Education
  - Youth Programs
- **FGC Website** (external link)
- **Contact** page (top-level)

### Command Options

```bash
# Delete existing scaffolded content before creating new
python manage.py scaffold_navbar_content --delete

# Only create pages, skip navigation menu configuration
python manage.py scaffold_navbar_content --skip-menu

# View help
python manage.py scaffold_navbar_content --help
```

## Configuration

Navigation menu is configured in **Wagtail Admin → Settings → Navigation Menu**.

### Menu Structure

The navigation menu uses StreamField blocks:

#### Page Link
Links to a Wagtail page. Automatically:
- Uses page title as link text
- Marks current page with `aria-current="page"`
- Supports translations (links to translated version in current locale)

#### External Link
Links to an external URL. Requires:
- **URL**: Full URL including `https://`
- **Title**: Display text for the link

#### Dropdown Menu
Creates a dropdown with nested menu items. Contains:
- **Title**: Display text for the dropdown button
- **Items**: StreamField of PageLink or ExternalLink blocks
- **Limitation**: Maximum 2 levels (no nested dropdowns)

## Development

### Running Tailwind CSS Watcher

The navigation uses Tailwind CSS and DaisyUI components. For development:

```bash
# Terminal 1 - Django server
cd src
python manage.py runserver

# Terminal 2 - Tailwind watcher (auto-rebuild CSS)
cd src/theme/static_src
npm run dev
```

### Testing

Run navigation tests:

```bash
cd src
python manage.py test navigation
```

## Architecture

### Templates

- `navigation/navigation.html` - Main navigation template with desktop + mobile layouts
- Separate rendering for desktop (menubar with hover) and mobile (drawer with touch)

### Template Tags

- `{% navigation_menu %}` - Renders the navigation menu
- Auto-handles locale-aware translation lookup
- Optimized with prefetching to avoid N+1 queries

### Models

- `NavigationMenuSetting` - Site-wide navigation configuration (BaseSiteSetting)
- Stores menu structure as StreamField

### Blocks

See `navigation/blocks.py`:
- `PageLinkBlock` - ChoiceBlock for selecting Wagtail pages
- `ExternalLinkBlock` - StructBlock with URL + title fields
- `MenuItemBlock` - StreamBlock for dropdown items (page_link or external_link only)
- `DropdownMenuBlock` - StructBlock with title + items
- `TopLevelMenuBlock` - StreamBlock for top-level menu (page_link, external_link, or dropdown)

### Performance

- **Page prefetching**: Collects all page IDs and fetches in single query
- **Translation prefetching**: Fetches translations for current + default locale only
- **Cache dictionary**: O(1) lookup for translations during rendering

### Accessibility

- Desktop: `role="menubar"` with `role="menuitem"`
- Mobile: Drawer with semantic navigation landmarks
- Skip link: Hidden until focused (WCAG 2.1 AA)
- Keyboard navigation: Full support with focus indicators
- ARIA: Proper labels, expanded states, current page indicators

## Styling

Uses DaisyUI components:
- `navbar` - Main navigation bar
- `drawer` - Mobile slide-out menu
- `menu` - Menu list with horizontal/vertical variants
- `dropdown` - Dropdown menu with hover support
- `btn` - Buttons with ghost variant for hamburger icon

Custom styling:
- `bg-gray-50 shadow` - Subtle background for navbar
- `z-50` - Proper stacking for dropdowns
- Edge detection prevents dropdowns from going off-screen

## Future Enhancements

Potential improvements:
- Multi-level dropdowns (3+ levels)
- Mega menus with rich content
- Icons/images in menu items
- Menu item ordering/sorting in admin
- Per-locale navigation menus
- Menu item visibility rules (logged in/out, user roles)
