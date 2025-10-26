# Implementation Plan: Tailwind CSS Integration

**Branch**: `001-tailwind-integration` | **Date**: 2025-10-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-tailwind-integration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate Tailwind CSS v4 with DaisyUI component library and Typography plugin to provide professional styling for RichText content published by content managers. The primary requirement is enabling automatic typography styling for CMS content (articles, epistles, minutes, newsletters) without requiring content managers to manually apply CSS classes. Technical approach involves integrating django-tailwind package, creating a theme Django app, installing Tailwind plugins, and configuring development/production build workflows with live reload support.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Django 5.2+, Wagtail 7.0+, django-tailwind (latest), Node.js/npm (for Tailwind compilation)
**Storage**: N/A (styling layer, no data storage)
**Testing**: pytest-django (existing test framework), Django test runner
**Target Platform**: Web browsers (modern browsers with CSS Grid and Custom Properties support)
**Project Type**: Web application (Django + Wagtail CMS)
**Performance Goals**: CSS bundle <50KB gzipped, live reload within 2 seconds, page load increase <200ms
**Constraints**: Must not interfere with Wagtail admin styling, WCAG AA contrast ratios required, responsive 320px-2560px
**Scale/Scope**: Single-site styling system, affects all frontend templates, ~10-20 templates initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Centralized Constants Pattern

**Status**: COMPLIANT
**Rationale**: This feature adds styling configuration. Any theme-related constants (if needed) will be defined in the theme app's configuration file, not scattered across settings. django-tailwind manages its own configuration in the theme app, following the pattern of centralized configuration.

### ✅ II. Runtime Configuration First

**Status**: COMPLIANT
**Rationale**: While Tailwind compilation happens at build time, the CSS classes are applied in templates which can be modified without code changes. No runtime configuration needed for this styling layer. DaisyUI theme selection could be made runtime-configurable in future iterations if needed.

### ✅ III. Security First (NON-NEGOTIABLE)

**Status**: COMPLIANT
**Rationale**: This feature enhances the existing security posture. The prose classes will be applied to RichText content that is already sanitized by Wagtail's RichText field. No new user input vectors introduced. Templates will use standard Django template tags, not RawHTMLBlock.

### ✅ IV. Test-Driven Development

**Status**: COMPLIANT
**Rationale**: Tests will verify:

- Template rendering includes Tailwind CSS stylesheet tags
- Development build generates CSS file
- Production build optimizes and purges unused CSS
- Prose classes apply to RichText content
- No style conflicts with Wagtail admin

### ✅ V. Code Quality Standards

**Status**: COMPLIANT
**Rationale**: All Python code (settings updates, template tag usage) will follow existing pre-commit hooks (ruff, pyupgrade, django-upgrade). Template changes will be validated by djhtml and curlylint. No new code quality exceptions needed.

### ✅ VI. Migration Discipline

**Status**: N/A
**Rationale**: This feature does not introduce model changes, so no migrations are required. Purely a frontend styling enhancement.

### ✅ VII. Internationalization First

**Status**: COMPLIANT
**Rationale**: Tailwind CSS is language-agnostic. Typography plugin handles bidirectional text automatically. No impact on existing i18n functionality. Dark mode support enhances accessibility globally.

## Project Structure

### Documentation (this feature)

```text
specs/001-tailwind-integration/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output - N/A (no data models)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output - N/A (no API contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── theme/                      # NEW: Tailwind CSS theme app
│   ├── __init__.py
│   ├── apps.py
│   ├── static_src/             # Tailwind source files
│   │   └── src/
│   │       └── styles.css      # Main Tailwind CSS file with @import
│   ├── static/                 # Compiled CSS output (generated)
│   │   └── css/
│   │       └── dist/
│   │           └── styles.css  # Compiled Tailwind CSS
│   ├── templates/              # Theme templates
│   │   └── base.html           # Base template with Tailwind tags
│   ├── package.json            # Node dependencies
│   ├── package-lock.json       # Locked dependencies
│   └── tailwind.config.js      # Tailwind v4 config (if needed)
├── core/
│   ├── settings/
│   │   ├── base.py             # MODIFIED: Add theme app, tailwind settings
│   │   └── dev.py              # MODIFIED: Add django_browser_reload
│   ├── urls.py                 # MODIFIED: Add browser reload URL (dev only)
│   └── templates/
│       └── base.html           # MODIFIED: Extend theme base or add {% tailwind_css %}
├── content/
│   └── templates/
│       └── content/
│           └── content_page.html  # MODIFIED: Add prose classes to RichText
├── home/
│   └── templates/
│       └── home/
│           └── home_page.html     # MODIFIED: Add prose classes to RichText
└── manage.py

Procfile.tailwind               # NEW: Honcho process file for dev server
.gitignore                      # MODIFIED: Add node_modules/, theme/static/

tests/                          # No new test directories (use existing structure)
└── (use existing test structure in each app)
```

**Structure Decision**: This is a web application using Django + Wagtail. We follow Option 1 (single project) since both backend and frontend are in the same Django monolith. The theme app follows django-tailwind conventions with `static_src/` for source files and `static/` for compiled output. All existing Django apps remain unchanged except for template modifications to include Tailwind classes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: N/A - All constitution checks passed. No violations to justify.

## Phase 0: Research & Technology Decisions ✅

**Status**: COMPLETE
**Output**: [research.md](research.md)

### Decisions Made

1. **Integration Package**: django-tailwind with reload extras
2. **Tailwind Version**: v4 (latest, with @source directive)
3. **Component Library**: DaisyUI via plugin
4. **Typography**: @tailwindcss/typography plugin
5. **Development Workflow**: Combined server via `python manage.py tailwind dev`
6. **Production Build**: `python manage.py tailwind build` in deployment
7. **Template Strategy**: Wrap RichText content with prose classes
8. **Admin Isolation**: Scope Tailwind to frontend templates only
9. **Dark Mode**: CSS media query `prefers-color-scheme: dark`

All technical unknowns resolved. See research.md for detailed rationales and alternatives considered.

## Phase 1: Design & Contracts ✅

**Status**: COMPLETE

**Outputs**:

- data-model.md: N/A (no data models for styling layer)
- contracts/: N/A (no API contracts for styling layer)
- [quickstart.md](quickstart.md): Complete installation and usage guide
- Agent context: Updated via update-agent-context.sh

### Design Decisions

**Project Structure**:

- New Django app: `theme/` created by django-tailwind
- Source files: `theme/static_src/src/styles.css`
- Compiled output: `theme/static/css/dist/styles.css`
- Templates: Modified to include `{% tailwind_css %}` tag

**Configuration**:

- Settings: Add `tailwind` and `theme` to INSTALLED_APPS
- Development: Add `django_browser_reload` to dev settings
- URLs: Include browser reload endpoint in dev mode
- Procfile: Auto-generated for combined dev server

**Template Integration**:

- Base template: Add `{% tailwind_preload_css %}` and `{% tailwind_css %}`
- Content templates: Wrap RichText with `<article class="prose lg:prose-xl dark:prose-invert">`
- No changes to Wagtail admin templates

### Constitution Re-Check (Post-Design) ✅

All principles remain compliant after Phase 1 design:

- ✅ **Centralized Constants**: No configuration constants added; theme app handles its own config
- ✅ **Runtime Configuration**: No runtime config needed for CSS compilation
- ✅ **Security First**: No new user input vectors; styles applied to already-sanitized content
- ✅ **Test-Driven Development**: Test strategy defined for template rendering and CSS generation
- ✅ **Code Quality**: All changes follow existing pre-commit hooks
- ✅ **Migration Discipline**: No model changes, no migrations needed
- ✅ **Internationalization First**: Tailwind is language-agnostic, supports bidirectional text

**No violations introduced during design phase.**

## Phase 2: Task Breakdown

**Status**: NOT STARTED
**Next Command**: `/speckit.tasks`

The task breakdown phase will generate detailed implementation tasks based on the user stories, technical decisions, and design from Phases 0 and 1. Run `/speckit.tasks` to proceed.

## Implementation Summary

This implementation plan is complete through Phase 1. All research questions answered, design decisions made, and constitution compliance verified. The project is ready for task breakdown and implementation.

**Artifacts Generated**:

- ✅ plan.md (this file)
- ✅ research.md (technology decisions and best practices)
- ✅ quickstart.md (installation and usage guide)
- ✅ .github/copilot-instructions.md (updated agent context)

**Ready for**: `/speckit.tasks` command to generate implementation tasks
