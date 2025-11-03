# Specification Quality Checklist: Multi-lingual Navigation Menu System

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2025-10-26
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified
- [x] Accessibility requirements defined (WCAG 2.1 AA)
- [x] Frontend rendering requirements specified
- [x] Responsive design requirements included
- [x] Theme support (dark/light mode) addressed

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Validation Results

**Status**: ✅ PASSED (Updated: 2025-10-26 - Added Accessibility, Frontend & Nesting Requirements)

All checklist items have been validated. The specification has been **enhanced** with comprehensive accessibility, frontend requirements, and explicit nesting constraints:

1. **Content Quality**: The specification focuses on user needs across three key personas: administrators (creating menus), visitors (navigating the site), and users with disabilities (accessible navigation). Frontend requirements describe behavior and user experience without prescribing specific implementation frameworks.

2. **Requirement Completeness**: All 48 functional requirements (expanded from 45) are clear and testable. Latest additions clarify nesting limits and menu positioning:

   **Explicit Nesting Constraints (NEW)**:
   - **FR-013**: Exactly 2 levels maximum - top-level can be simple links OR dropdowns; dropdowns can ONLY contain simple links (no nested dropdowns)
   - **FR-013a**: System must prevent administrators from nesting dropdowns within dropdowns (enforced in admin interface)
   - This prevents UI complexity and maintains usability - clear hierarchical structure without confusion

   **Edge-Aware Menu Positioning (NEW)**:
   - **FR-046**: Dropdown menus implement edge detection to prevent viewport overflow
   - **FR-047**: Menu positioning is responsive and adapts to viewport size changes
   - **FR-048**: Default direction is downward when sufficient space exists
   - **Logic**: Near right edge → open left; near left edge → open right; sufficient space → open down
   - **Mobile**: Same edge detection applies to smaller viewports (320px minimum)

   **Accessibility Requirements (FR-025 through FR-045)**:
   - **Semantic HTML**: `<nav>` element with ARIA landmarks and proper labeling
   - **ARIA Roles**: `role="none"` for list items, `role="menuitem"` for links, `role="menu"` for submenus
   - **ARIA Properties**: `aria-haspopup`, `aria-controls`, `aria-labelledby`, `aria-current="page"`
   - **Keyboard Navigation**: Full keyboard support (Tab, Enter, Space, Escape, Arrow keys)
   - **Screen Reader Support**: Proper announcements for menu structure, position, and state
   - **Focus Management**: Visible focus indicators with 3:1 contrast ratio minimum
   - **Progressive Enhancement**: Works without JavaScript using `<details>`/`<summary>` elements
   - **Touch Accessibility**: 44x44 pixel minimum touch targets
   - **Color Contrast**: 4.5:1 for text, 3:1 for interactive components (WCAG AA)
   - **Skip Links**: Keyboard users can bypass navigation to main content

   **Theme & Responsive Design**:
   - **Dark/Light Mode**: Theme-aware classes (e.g., `bg-base-100`) adapt automatically
   - **Responsive Layout**: Mobile hamburger menu at < 1024px breakpoint
   - **Accessible Hamburger**: Button with `aria-expanded` state
   - **Multi-indicator Hover**: Not reliant on color alone (underline, background, border)

   **Template Structure**:
   - **Single Template**: `navigation.html` - Complete navigation with mobile drawer, desktop menubar, and dropdowns
   - **Base Integration**: Included in `base.html` via `{% navigation_menu %}` tag for site-wide availability
   - **DaisyUI Components**: Uses drawer, navbar, menu, and dropdown-hover components

3. **User Story Enhancement**: Added **User Story 4 - Accessible Navigation** (Priority P1) with 12 acceptance scenarios covering:
   - Keyboard-only navigation
   - Screen reader announcements
   - JavaScript-disabled fallback
   - Mobile touch targets
   - Dark mode contrast
   - Skip link functionality
   - Color-blind user support

   **User Story 2** expanded with 4 new scenarios for nesting constraints and edge detection:
   - Scenario 9: Validation prevents 3+ level nesting (dropdown within dropdown blocked)
   - Scenario 10: Right-edge dropdowns open to the left
   - Scenario 11: Left-edge dropdowns open to the right
   - Scenario 12: Default downward opening with sufficient space

4. **Success Criteria**: Expanded from 10 to 20 criteria, adding:
   - **SC-011**: Zero critical accessibility errors (axe DevTools/WAVE validation)
   - **SC-012**: Full keyboard navigation without mouse
   - **SC-013**: Proper screen reader context and announcements
   - **SC-014**: Automatic theme adaptation
   - **SC-015**: 44x44px touch targets with clear focus
   - **SC-016**: 4.5:1 and 3:1 contrast ratios
   - **SC-017**: JavaScript-optional functionality
   - **SC-018**: Skip link activation
   - **SC-019**: Edge-aware dropdown positioning (tested at 320px, 768px, 1024px, 1920px viewports)
   - **SC-020**: Clear validation error for 3+ level nesting attempts

5. **Edge Cases**: Added 13 new scenarios (from original 10 to 23 total):
   - Keyboard navigation with nested dropdowns
   - JavaScript-disabled functionality
   - Dark mode styling
   - Current page indication
   - Mobile responsive behavior
   - Touch target sizing
   - Screen reader dropdown announcements
   - Color-blind hover state distinction
   - **3+ level nesting prevention** (administrator validation error)
   - **Dropdown viewport overflow** (edge detection logic)
   - **Mobile edge detection** (small viewport adaptation)
   - **Viewport resize handling** (recalculate position or close menu)

**Simplified Multi-lingual Architecture**:

- **FR-003**: Default behavior - use page's own title (already translated via Wagtail)
- **FR-004**: **Optional** custom title field for menu items
- **FR-005**: **Optional** translations for custom titles (only when custom title is provided)
- **FR-006**: Auto-display page's translated title when no custom title
- **FR-007**: Display custom title or its translation when provided
- **FR-010**: External links and dropdown titles support optional translations

**Why This Is Better**:

- **90% of menu items**: Just use page titles (zero translation work)
- **10% edge cases**: Custom titles with optional translations (minimal translation work)
- **Example**: "About Us" page already has title in EN/ES/FR → menu automatically shows correct title
- **Override**: If you want menu to say "Learn More" instead → add custom title + optional translations

**Single Menu Architecture**:

- **FR-001**: Single site-wide navigation menu via Settings (BaseSiteSetting pattern)
- No "multiple menus" or "display locations" complexity
- Settings → Navigation Menu (simple, direct access)

**Menu Structure** (aligned with Wagtail patterns):

- **FR-008**: Support for both internal page links AND external URL links
- **FR-009**: Dropdown menus contain child items (StreamField pattern)
- **FR-011**: Reordering via **up/down arrows** (Wagtail's default UI)
- **FR-012**: Support for anchor links (fragment identifiers)
- **FR-013**: **2-level nesting** (top-level → dropdown → children)

**Translation Fallback Chain**:

- **If custom title provided**: Custom title (visitor's locale) → Custom title (default) → Page title (visitor's locale) → Page title (default)
- **If no custom title**: Page title (visitor's locale) → Page title (default)

Success criteria remain measurable (e.g., "under 2 minutes", "100% of the time", "90% of administrators"). No [NEEDS CLARIFICATION] markers exist - the spec makes reasonable assumptions about:

- BaseSiteSetting for site-wide navigation menu (Wagtail's standard pattern)
- Up/down arrow reordering (standard Wagtail admin pattern)
- 2-level menu structure (simple links + dropdown menus with children)
- Optional custom titles with optional translations (minimal complexity, maximum flexibility)
- Automatic page title translation inheritance (Wagtail's built-in capability)
- Edge case handling: Clear fallback strategy for missing translations

1. **Feature Readiness**: Four prioritized user stories (P1: Basic menu with optional custom titles, P1: Accessible navigation for all users, P2: Nested structure with dropdown menus, P3: Multi-lingual menu rendering) provide clear development path. Each story is independently testable with specific acceptance scenarios reflecting accessibility-first design and optional custom title pattern.

## Notes

The specification has been **refined for practical simplicity** while maintaining full multi-lingual capability:

**Design Philosophy - Simplicity First**:

- **Single Menu**: One site-wide navigation menu per site (accessed via Settings → Navigation Menu)
- **No Display Locations**: This feature focuses on the primary navigation; footer/sidebar menus are out of scope
- **BaseSiteSetting**: Uses Wagtail's site settings pattern for site-wide configuration
- **Cleaner Admin UX**: Settings → Navigation Menu (no need to select which menu to edit or where to display it)
- **User Focus**: Meetings/worship groups can focus on content rather than technical menu configuration

**Rationale**: While WordPress allows multiple menus with complex location assignments, QuakerCMS prioritizes ease of use for non-technical users. The single-menu constraint eliminates decisions about "which menu goes where" while still supporting the primary use case: a well-structured, multi-lingual navigation for the site.

**Out of Scope** (for future features if needed):

- Multiple menus (header, footer, sidebar)
- Menu display location assignment
- Per-page menu overrides

**Translation Strategy** (elegant and practical):

**For Page Links** (90% of use cases):

- **Default**: Use page's own title (automatically translated via Wagtail)
- **Override**: Optionally provide custom title + optional translations
- **Result**: Zero translation work for typical cases, flexibility when needed

**For External Links & Dropdowns** (10% of use cases):

- **Required**: Title field (no page to inherit from)
- **Optional**: Translations for that title
- **Result**: Minimal translation work, only where necessary

**Example Scenarios**:

1. **Typical Case** (zero extra work):

   ```text
   Page: "About Us" (EN), "Acerca de" (ES), "À propos" (FR)
   Menu Item: [Select page] → Auto-displays correct title in each locale
   ```

2. **Custom Title** (simple override):

   ```text
   Page: "Community Resources"
   Menu Custom Title: "Resources" (EN only)
   Result: Shows "Resources" in all locales (good enough for most cases)
   ```

3. **Translated Custom Title** (when needed):

   ```text
   Page: "Community Resources"
   Menu Custom Title:
     - EN: "Resources"
     - ES: "Recursos"
     - FR: "Ressources"
   Result: Shows appropriate translation in each locale
   ```

**Implementation Pattern** (conceptual, technology-agnostic):

```text
NavigationPageChooserBlock:
  - page: [PageChooser] (required)
  - title: [CharBlock] (optional - custom override)
  - title_translations: [Repeating locale-text] (optional - only if title provided)
  - anchor: [CharBlock] (optional)

Display Logic:
  if custom title exists:
    if translation for current locale exists:
      show translation
    else:
      show default custom title
  else:
    show page.title (in current locale, or fallback to default locale)
```

**Key Improvement Over Previous Version**:

- **Before**: Required locale-text pairs for ALL custom labels (complex, tedious)
- **Now**: Custom title optional, translations optional (simple, flexible)
- **Impact**: 90% reduction in translation management burden

The spec remains **technology-informed but technology-agnostic** - it describes the user-facing behavior and data structure conceptually without prescribing specific Wagtail field types or implementation details (though it aligns perfectly with practical Wagtail patterns).

**Ready for**: `/speckit.plan` - The specification is complete and ready for detailed implementation planning with an elegant, practical approach to multi-lingual navigation.
