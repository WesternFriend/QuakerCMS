# Implementation Plan: Multi-lingual Navigation Menu System

**Branch**: `002-nav-menu-system` | **Date**: 2025-10-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-nav-menu-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a site-wide navigation menu system with multi-lingual support, accessible administration interface, and full WCAG 2.1 AA compliance. The system allows administrators to create simple menus with top-level items (either simple links or dropdown menus). Dropdowns can contain only simple links, limiting menu depth to 2 levels maximum. Menus automatically adapt to visitor locale with graceful fallback for untranslated content. Frontend uses DaisyUI components for responsive mobile-first design with hamburger drawer on mobile devices.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Django 5.2+, Wagtail 7.0+, DaisyUI (via django-tailwind)
**Storage**: SQLite (dev) / PostgreSQL (production) - standard Django ORM
**Testing**: pytest with Django plugin, organized by feature (ModelTests, StreamFieldTests, AdminTests, IntegrationTests)
**Target Platform**: Web application (responsive, mobile-first)
**Project Type**: Django/Wagtail CMS application
**Performance Goals**: < 100ms menu rendering for up to 50 menu items
**Constraints**: WCAG 2.1 AA compliance (mandatory), 2-level menu nesting maximum, single site-wide menu only
**Scale/Scope**: 1-50 menu items typical, support for 19+ locales, site-wide setting (not per-page)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Centralized Constants Pattern ✅

- **Compliance**: Navigation menu uses Wagtail's BaseSiteSetting (database-driven configuration)
- **No new constants needed**: Menu structure stored in database, not code constants
- **Imports properly**: Will use existing `core.constants` for any locale-related logic

### II. Runtime Configuration First ✅

- **Compliance**: Menu configured via Wagtail admin Settings → Navigation Menu
- **Database-driven**: NavigationMenuSetting model stores all menu structure
- **No restart required**: Menu changes take effect immediately (standard Wagtail behavior)
- **Graceful fallback**: Empty menu = no `<nav>` element rendered

### III. Security First ✅

- **Compliance**: Uses only safe StreamField blocks (PageChooserBlock, URLBlock, StructBlock)
- **NO RawHTMLBlock**: Specification explicitly requires EmbedBlock for embedded content
- **Input sanitization**: Django/Wagtail framework handles all user input sanitization
- **External URL validation**: Basic format validation (http/https) in admin field

### IV. Test-Driven Development ✅

- **Compliance**: Spec includes comprehensive acceptance scenarios for all user stories
- **Test organization**: Will follow standard pattern (ModelTests, StreamFieldTests, AdminTests, TranslationTests, IntegrationTests)
- **Coverage required**: Menu creation, nesting, locale switching, edge cases (deleted pages, empty menus)
- **Accessibility tests**: WCAG compliance verification via automated tools (axe DevTools)

### V. Code Quality Standards ✅

- **Compliance**: Pre-commit hooks already configured (ruff, pyupgrade, django-upgrade, djhtml, curlylint)
- **Auto-enforcement**: All code will pass through existing quality gates
- **Template quality**: Navigation templates will be linted by curlylint and djhtml

### VI. Migration Discipline ✅

- **Compliance**: NavigationMenuSetting model requires migration
- **StreamField changes**: All menu item block structures will generate migrations
- **Version control**: All migrations committed to git
- **Reversible**: Standard Django migration patterns ensure rollback capability

### VII. Internationalization First ✅

- **Compliance**: Multi-lingual support is PRIMARY feature requirement (User Story 3, Priority P3)
- **Runtime adjustable**: Uses existing LocaleSettings for language configuration
- **Per-locale content**: Menu items link to locale-specific page translations
- **19+ languages**: Leverages existing locale support from core.constants
- **Fallback strategy**: Untranslated pages fall back to default locale (spec requirement)

**GATE STATUS**: ✅ **PASS** - All constitutional principles satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/002-nav-menu-system/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── navigation-api.md  # Menu rendering contract (template context)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── navigation/          # NEW: Navigation menu app
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py       # NavigationMenuSetting with StreamField
│   ├── admin.py        # Admin customization (if needed)
│   ├── blocks.py       # Menu item StreamField blocks
│   ├── tests.py        # Comprehensive test suite
│   ├── migrations/
│   │   └── 0001_initial.py
│   └── templates/
│       └── navigation/
│           ├── navigation.html          # Main nav component
│           ├── navigation_item.html     # Simple link block
│           └── navigation_dropdown.html # Dropdown menu block
├── core/
│   ├── templates/
│   │   ├── base.html   # MODIFIED: Include navigation component
│   │   └── components/
│   │       └── navigation.html  # May be moved here from navigation app
│   └── settings/
│       └── base.py     # MODIFIED: Add 'navigation' to INSTALLED_APPS
└── theme/
    └── static_src/
        └── src/
            └── styles.css  # MODIFIED: Add navigation-specific Tailwind classes if needed

tests/                   # Integration tests may go here
```

**Structure Decision**: Single Django app approach (navigation app). Following QuakerCMS pattern where each feature is a self-contained Django app under `src/`. Templates may be moved to `core/templates/components/` for site-wide availability, following the existing pattern in the codebase.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - This section is not applicable. All constitutional principles are satisfied without exceptions.

---

## Phase Completion Status

### Phase 0: Outline & Research ✅

**Status**: Complete

**Artifacts Generated**:
- ✅ `research.md` - Comprehensive technical research covering:
  - Wagtail StreamField architecture for navigation menus
  - DaisyUI drawer component implementation
  - WCAG 2.1 AA navigation patterns
  - Multi-lingual menu rendering strategies
  - StreamField nesting limit enforcement

**Key Decisions**:
1. Use StreamField with MenuItemBlock limiting children to PageLinkBlock and ExternalLinkBlock only (enforces 2-level maximum)
2. DaisyUI drawer component (left-side) for mobile navigation
3. ARIA menubar pattern for desktop, menu pattern for mobile
4. Runtime locale resolution with fallback chain
5. Progressive enhancement with `<details>` element

**Unknowns Resolved**: All technical unknowns identified and resolved. No NEEDS CLARIFICATION items remain.

---

### Phase 1: Design & Contracts ✅

**Status**: Complete

**Artifacts Generated**:
- ✅ `data-model.md` - Complete data model specification:
  - NavigationMenuSetting model (BaseSiteSetting)
  - 5 StreamField blocks (TopLevelMenuBlock with PageLinkBlock, ExternalLinkBlock, DropdownMenuBlock containing MenuItemBlock)
  - Block structure enforces 2-level maximum (no nested dropdowns)
  - Database schema and migration plan
  - Query patterns and data volume estimates

- ✅ `contracts/navigation-api.md` - API contract specification:
  - Template tag interface (`{% navigation_menu %}`)
  - Data structure contracts (MenuItem types)
  - Template context examples (basic, nested, multi-lingual)
  - ARIA requirements and accessibility contract
  - Performance targets and caching strategy

- ✅ `quickstart.md` - Developer implementation guide:
  - Step-by-step installation instructions
  - Complete code examples for all components
  - Testing setup and verification steps
  - Troubleshooting guide

**Agent Context Updated**: ✅
- Updated `.github/copilot-instructions.md` with new technologies:
  - Python 3.12+
  - Django 5.2+, Wagtail 7.0+, DaisyUI (via django-tailwind)
  - SQLite (dev) / PostgreSQL (production)

**Constitution Re-check**: ✅ **PASS** - All principles remain satisfied after design phase.

---

### Phase 2: Task Breakdown ⏳

**Status**: Pending - Use `/speckit.tasks` command to generate

**Expected Output**: `tasks.md` with breakdown of implementation tasks organized by:
- Backend implementation (models, blocks, template tags)
- Frontend implementation (templates, accessibility)
- Testing (unit, integration, accessibility)
- Documentation updates

---

## Next Steps

1. **Run task generation**: Execute `/speckit.tasks` to break down implementation into actionable tasks
2. **Review tasks**: Ensure all acceptance criteria from spec are covered
3. **Begin implementation**: Follow quickstart guide and task checklist
4. **Test continuously**: Run tests as each component is built
5. **WCAG validation**: Run accessibility scans throughout development

---

## Summary

**Planning Phase**: ✅ Complete (Phases 0-1)
**Constitutional Compliance**: ✅ All 7 principles satisfied
**Documentation**: ✅ 4 artifacts generated (research, data-model, contracts, quickstart)
**Ready for**: ✅ Task breakdown and implementation

**Branch**: `002-nav-menu-system`
**Specification**: [spec.md](./spec.md)
**Implementation Plan**: This file
**Next Command**: `/speckit.tasks` to generate task breakdown
