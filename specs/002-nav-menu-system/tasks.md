# Tasks: Multi-lingual Navigation Menu System

**Feature**: Multi-lingual Navigation Menu System
**Branch**: `002-nav-menu-system`
**Generated**: 2025-10-26
**Status**: Ready for Implementation

## Overview

This document breaks down the navigation menu implementation into discrete, executable tasks organized by user story. Each phase represents a complete, independently testable increment of functionality.

## Task Organization

Tasks are organized by user story priority (P1, P2, P3) to enable incremental delivery:

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (shared infrastructure)
- **Phase 3**: User Story 1 - Basic Navigation Menu (P1)
- **Phase 4**: User Story 4 - Accessible Navigation (P1)
- **Phase 5**: User Story 2 - Dropdown Menus (P2)
- **Phase 6**: User Story 3 - Multi-lingual Support (P3)
- **Phase 7**: Polish & Cross-Cutting Concerns

**Note**: User Story 4 (Accessibility) is implemented alongside User Story 1 since accessibility must be built in from the start, not retrofitted.

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**MVP = Phase 1-4** (User Story 1 + User Story 4)
- Basic menu with top-level page links
- WCAG 2.1 AA accessibility compliance
- Mobile responsive with hamburger menu
- Keyboard navigation support
- Screen reader compatibility

**Why this MVP**: Delivers immediately useful navigation while establishing accessibility foundation. Can be deployed to production and enhanced incrementally.

### Incremental Delivery Path

1. **Sprint 1** (Phases 1-4): MVP - Basic accessible navigation
2. **Sprint 2** (Phase 5): Dropdown menus for content organization
3. **Sprint 3** (Phase 6): Multi-lingual support for international sites
4. **Sprint 4** (Phase 7): Polish, performance optimization, documentation

## Parallel Execution Opportunities

Tasks marked with **[P]** can be executed in parallel with other tasks in the same phase (different files, no dependencies).

### Phase 3 Parallelization Example (User Story 1)
After T006 completes, the following can run in parallel:
- T007 [P] - Create blocks.py
- T008 [P] - Create models.py
- T009 [P] - Create template tag skeleton

### Phase 5 Parallelization Example (User Story 2)
- T019 [P] - Add dropdown CSS styles
- T020 [P] - Add mobile drawer styles
- T021 [P] - Implement edge detection JavaScript

## Dependencies

### User Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: Basic Menu) ← MUST complete first
    ↓
Phase 4 (US4: Accessibility) ← Builds on Phase 3
    ↓
Phase 5 (US2: Dropdowns) ← Requires Phase 3+4
    ↓
Phase 6 (US3: Multi-lingual) ← Can build on Phase 3+4 (independent of Phase 5)
    ↓
Phase 7 (Polish)
```

**Key Dependencies**:
- Phase 3 blocks all other user stories (foundational menu system)
- Phase 4 should complete before Phase 5 (accessibility patterns established)
- Phase 6 is independent of Phase 5 (can be developed in parallel if needed)

---

## Phase 1: Setup

**Goal**: Initialize navigation app and configure Django settings

**Independent Test**: Navigation app exists, is registered in INSTALLED_APPS, and passes `python manage.py check`

### Tasks

- [ ] T001 Create navigation app using startapp command in src/ directory
- [ ] T002 Add 'navigation' to INSTALLED_APPS in src/core/settings/base.py
- [ ] T003 Create src/navigation/templatetags/ directory with __init__.py
- [ ] T004 Create src/navigation/templates/navigation/ directory structure
- [ ] T005 Run Django check command to verify app configuration

---

## Phase 2: Foundational

**Goal**: Set up shared infrastructure and base classes

**Independent Test**: Migrations run successfully, no import errors when importing blocks module

### Tasks

- [ ] T006 Create src/navigation/__init__.py and src/navigation/apps.py with AppConfig

---

## Phase 3: User Story 1 - Basic Navigation Menu (P1)

**Story Goal**: Site administrators can create a simple navigation menu with top-level page links that display correctly on the front-end with proper links and labels.

**Independent Test**:
1. Create menu with 3-5 top-level page links in admin
2. Save menu and verify it displays on front-end
3. Click links and verify navigation to correct pages
4. Verify custom titles display when provided
5. Verify page titles display when custom title is blank

**Acceptance Scenarios Covered**: US1 scenarios 1-8 (admin interface, page links, custom titles, ordering, navigation)

### Tasks

- [ ] T007 [P] [US1] Create PageLinkBlock in src/navigation/blocks.py with page, custom_title, and anchor fields
- [ ] T008 [P] [US1] Create ExternalLinkBlock in src/navigation/blocks.py with url, title, and anchor fields
- [ ] T009 [P] [US1] Create TopLevelMenuBlock StreamBlock in src/navigation/blocks.py allowing page_link and external_link
- [ ] T010 [P] [US1] Create StreamFieldTests class in src/navigation/tests.py to test block structure and field validation
- [ ] T011 [US1] Create NavigationMenuSetting model in src/navigation/models.py with menu_items StreamField using TopLevelMenuBlock
- [ ] T012 [US1] Register NavigationMenuSetting as BaseSiteSetting with @register_setting decorator in src/navigation/models.py
- [ ] T013 [US1] Create and run migration for NavigationMenuSetting model
- [ ] T014 [P] [US1] Create ModelTests class in src/navigation/tests.py to test NavigationMenuSetting creation and validation
- [ ] T015 [US1] Create navigation_tags.py in src/navigation/templatetags/ with navigation_menu inclusion tag
- [ ] T016 [US1] Implement process_menu_item() helper function in navigation_tags.py to handle page_link and external_link types
- [ ] T017 [US1] Add locale resolution logic to process_menu_item() with fallback to default locale
- [ ] T018 [US1] Create basic navigation.html template in src/navigation/templates/navigation/ with desktop menu structure
- [ ] T019 [US1] Add {% navigation_menu %} tag to src/core/templates/base.html below skip link
- [ ] T020 [US1] Test basic menu creation in admin and verify front-end display with multiple page links
- [ ] T021 [P] [US1] Create IntegrationTests class in src/navigation/tests.py to test end-to-end menu rendering with page links

---

## Phase 4: User Story 4 - Accessible Navigation (P1)

**Story Goal**: Visitors using assistive technology can navigate the site independently with full keyboard support, screen reader compatibility, and WCAG 2.1 AA compliance.

**Independent Test**:
1. Navigate menu using only keyboard (Tab, Enter, Escape)
2. Test with NVDA/JAWS screen reader for proper announcements
3. Test with JavaScript disabled (progressive enhancement)
4. Run axe DevTools accessibility scan (zero critical errors)
5. Test on mobile device (touch target sizes, hamburger menu)
6. Test in dark/light themes (contrast ratios)

**Acceptance Scenarios Covered**: US4 scenarios 1-12 (keyboard navigation, screen reader, mobile, dark mode, skip link, contrast)

### Tasks

- [ ] T022 [P] [US4] Add skip link to src/core/templates/base.html with sr-only and focus styles
- [ ] T023 [P] [US4] Add ARIA attributes to navigation.html (role="menubar", aria-label="Main navigation")
- [ ] T024 [P] [US4] Add role="none" to menu list items and role="menuitem" to links in navigation.html
- [ ] T025 [P] [US4] Add aria-current="page" attribute to current page menu item in navigation.html
- [ ] T026 [P] [US4] Create AccessibilityTests class in src/navigation/tests.py for ARIA attribute validation
- [ ] T027 [P] [US4] Create mobile hamburger menu structure with DaisyUI drawer in navigation.html
- [ ] T028 [P] [US4] Add drawer checkbox with id="nav-drawer" and corresponding labels in navigation.html
- [ ] T029 [P] [US4] Add aria-expanded and aria-controls attributes to hamburger button in navigation.html
- [ ] T030 [P] [US4] Style navigation with DaisyUI theme-aware classes (bg-base-100, text-base-content) in navigation.html
- [ ] T031 [P] [US4] Add focus indicators with sufficient contrast (ring-2 ring-primary) to all interactive elements
- [ ] T032 [US4] Test keyboard navigation (Tab through items, verify focus indicators visible)
- [ ] T033 [US4] Test screen reader with NVDA or JAWS (verify menu announcements)
- [ ] T034 [US4] Run axe DevTools accessibility scan and fix critical errors
- [ ] T035 [US4] Test mobile hamburger menu on device <1024px (verify drawer opens/closes)
- [ ] T036 [US4] Verify touch target sizes are minimum 44x44 pixels on mobile
- [ ] T037 [US4] Test dark mode theme switching (verify contrast ratios)
- [ ] T038 [US4] Test with JavaScript disabled (basic links should still work)

---

## Phase 5: User Story 2 - Dropdown Menus (P2)

**Story Goal**: Site administrators can create dropdown menus to group related pages hierarchically, with proper hover/click behavior on desktop and accordion-style expansion on mobile.

**Independent Test**:
1. Create menu with at least one dropdown containing 3+ child items
2. Verify dropdown opens on hover (desktop ≥1024px)
3. Verify dropdown opens on click (all devices)
4. Verify child items navigate correctly
5. Test dropdown positioning near screen edges (left/right)
6. Test accordion expansion in mobile drawer

**Acceptance Scenarios Covered**: US2 scenarios 1-11 (dropdown creation, translations, reordering, hover/click, positioning)

### Tasks

- [ ] T039 [P] [US2] Create MenuItemBlock StreamBlock in src/navigation/blocks.py allowing only page_link and external_link
- [ ] T040 [P] [US2] Create DropdownMenuBlock StructBlock in src/navigation/blocks.py with title and items (MenuItemBlock)
- [ ] T041 [US2] Add dropdown block type to TopLevelMenuBlock in src/navigation/blocks.py
- [ ] T042 [US2] Create and run migration for dropdown menu block structure
- [ ] T043 [US2] Update process_menu_item() in navigation_tags.py to handle dropdown type
- [ ] T044 [US2] Add child item processing logic to dropdown handler with is_open calculation
- [ ] T045 [P] [US2] Add desktop dropdown menu HTML with dropdown-hover class to navigation.html
- [ ] T046 [P] [US2] Add ARIA attributes for dropdowns (aria-haspopup, aria-controls, aria-labelledby) to navigation.html
- [ ] T047 [P] [US2] Add mobile accordion dropdown using <details>/<summary> in drawer section of navigation.html
- [ ] T048 [P] [US2] Add chevron/arrow icons to indicate dropdown state in navigation.html
- [ ] T049 [P] [US2] Implement JavaScript dropdown edge detection in navigation.html (check viewport bounds, adjust positioning left/right)
- [ ] T050 [US2] Test dropdown creation in admin with 3+ child items
- [ ] T051 [US2] Test desktop dropdown opens on hover (≥1024px viewport)
- [ ] T052 [US2] Test desktop dropdown opens on click (accessibility)
- [ ] T053 [US2] Test mobile accordion expansion in drawer (<1024px viewport)
- [ ] T054 [US2] Test dropdown positioning near right edge (should open left)
- [ ] T055 [US2] Test dropdown positioning near left edge (should open right)
- [ ] T056 [US2] Test menu reordering using Wagtail StreamField built-in up/down arrow controls in admin
- [ ] T057 [P] [US2] Add dropdown tests to StreamFieldTests class in src/navigation/tests.py

---

## Phase 6: User Story 3 - Multi-lingual Support (P3)

**Story Goal**: Menus automatically adapt to visitor's language with graceful fallback when translations are missing, ensuring consistent navigation across all locales.

**Independent Test**:
1. Create menu in default locale (English) with 5 pages
2. Translate 3 of those pages to Spanish
3. Switch site to Spanish locale
4. Verify 3 translated pages link to Spanish versions
5. Verify 2 untranslated pages link to English versions (fallback)
6. Verify menu labels use translated page titles or custom title translations

**Acceptance Scenarios Covered**: US3 scenarios 1-9 (locale detection, page translation linking, custom title translations, fallback behavior)

### Tasks

- [ ] T058 [P] [US3] Add Locale.get_active() call to navigation_menu template tag in navigation_tags.py
- [ ] T059 [P] [US3] Add Locale.get_default() fallback logic to navigation_menu template tag
- [ ] T060 [US3] Update process_menu_item() to resolve page translations using page.localized.get(locale=current_locale)
- [ ] T061 [US3] Add try/except fallback to default locale when page translation doesn't exist in process_menu_item()
- [ ] T062 [US3] Filter out deleted/unpublished pages in all locales in process_menu_item()
- [ ] T063 [US3] Update title resolution to use translated page title when no custom_title in process_menu_item()
- [ ] T064 [US3] Test menu with mix of translated and untranslated pages (verify fallback)
- [ ] T065 [US3] Test switching between locales (verify menu adapts automatically)
- [ ] T066 [US3] Test custom title translations in multiple locales
- [ ] T067 [US3] Test page translation addition/removal (verify menu updates)
- [ ] T068 [P] [US3] Create TranslationTests class in src/navigation/tests.py to test locale switching and fallback behavior

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Performance optimization, comprehensive testing, documentation updates, and production readiness.

**Independent Test**: All tests pass, WCAG validation passes, performance targets met (<100ms rendering), documentation complete.

### Tasks

- [ ] T069 [P] Add AdminTests class to src/navigation/tests.py to test menu creation and editing in admin interface
- [ ] T070 Run full test suite and achieve >90% code coverage
- [ ] T071 [P] Add performance optimization comments to navigation_tags.py for caching strategy
- [ ] T072 [P] Update .github/copilot-instructions.md with navigation patterns and examples
- [ ] T073 [P] Add navigation section to project README.md with usage examples
- [ ] T074 Run final WCAG 2.1 AA validation scan with axe DevTools
- [ ] T075 Test menu with 50 items to verify <100ms rendering performance target
- [ ] T076 Test all edge cases from spec (deleted pages, empty menu, invalid URLs)
- [ ] T077 Create CHANGELOG entry documenting navigation menu feature
- [ ] T078 Final code quality check (ruff, pre-commit hooks)

---

## Task Summary

**Total Tasks**: 78
**MVP Tasks** (Phases 1-4): 38 tasks
**Full Feature Tasks** (Phases 1-7): 78 tasks

**Task Distribution by User Story**:
- Setup (Phase 1): 5 tasks
- Foundational (Phase 2): 1 task
- User Story 1 - Basic Menu (P1): 15 tasks (includes ModelTests, StreamFieldTests, IntegrationTests)
- User Story 4 - Accessibility (P1): 17 tasks (includes AccessibilityTests)
- User Story 2 - Dropdowns (P2): 19 tasks (includes edge detection implementation and tests)
- User Story 3 - Multi-lingual (P3): 11 tasks (includes TranslationTests)
- Polish & Cross-Cutting (Phase 7): 10 tasks

**Parallel Opportunities**: 28 tasks marked [P] can execute in parallel

**Test Coverage**: Tests integrated throughout phases (TDD approach) - ModelTests (T014), StreamFieldTests (T010, T057), AccessibilityTests (T026), TranslationTests (T068), IntegrationTests (T021), AdminTests (T069)

**Estimated Timeline**:
- MVP (Phases 1-4): 4-6 days (includes integrated testing)
- Full Feature (Phases 1-7): 8-11 days
- Per Sprint: ~2-3 days with single developer

**TDD Compliance**: ✅ Tests now integrated within implementation phases per Constitution Principle IV

---

## Validation Checklist

Before marking the feature complete, verify:

- [ ] All 78 tasks completed and checked off
- [ ] All user stories (US1, US2, US3, US4) acceptance scenarios pass
- [ ] WCAG 2.1 AA validation passes with zero critical errors
- [ ] All tests pass with >90% coverage
- [ ] Test classes implemented: ModelTests, StreamFieldTests, AccessibilityTests, TranslationTests, IntegrationTests, AdminTests
- [ ] Performance target met (<100ms rendering for 50 items)
- [ ] Documentation updated (README, AGENTS.md, CHANGELOG)
- [ ] Code quality checks pass (ruff, pre-commit)
- [ ] Manual testing complete on desktop and mobile
- [ ] Screen reader testing complete (NVDA or JAWS)
- [ ] Multi-browser testing complete (Chrome, Firefox, Safari)

---

## Next Steps

1. **Review this task breakdown** with team to confirm scope and timeline
2. **Begin Phase 1** (Setup tasks T001-T005)
3. **Track progress** by checking off tasks as completed
4. **Test incrementally** after each phase completes
5. **Deploy MVP** after Phase 4 completes (immediate value)
6. **Continue with enhancements** (Phases 5-7) based on priority

**Ready to begin implementation!** 🚀

Follow the quickstart.md guide for detailed code examples and implementation patterns.
