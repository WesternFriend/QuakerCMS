<!--
SYNC IMPACT REPORT
==================
Version: 1.0.0 (Initial Constitution)
Ratified: 2025-10-26
Last Amended: 2025-10-26

CHANGES IN THIS VERSION:
- Initial constitution ratified for QuakerCMS project
- Established 7 core principles based on project architecture and standards
- Defined technology stack and development workflow requirements

PRINCIPLES DEFINED:
1. Centralized Constants Pattern (architectural integrity)
2. Runtime Configuration (flexibility without code changes)
3. Security First (XSS protection, safe content handling)
4. Test-Driven Development (quality assurance)
5. Code Quality Standards (automated enforcement)
6. Migration Discipline (database integrity)
7. Internationalization First (global accessibility)

TEMPLATES STATUS:
✅ plan-template.md - Constitution Check section aligns with principles
✅ spec-template.md - Requirements structure supports principle validation
✅ tasks-template.md - Task categorization reflects principle-driven development
✅ AGENTS.md - Runtime guidance fully aligned with constitution

FOLLOW-UP TODOS:
- None - all placeholders resolved

-->

# QuakerCMS Constitution

A specialized content management system for Quaker communities worldwide, emphasizing runtime
configurability, internationalization, and secure content management.

## Core Principles

### I. Centralized Constants Pattern

**ALL configuration constants MUST be defined in a single source of truth.**

- Language/i18n constants MUST be defined ONLY in `src/core/constants.py`
- Settings files MUST import from constants, never define constants directly
- Models MUST use constants for choices, never hardcode values
- Rationale: Prevents drift between settings, models, and utilities. Ensures consistency across
  Django settings (`settings/base.py`), model choices (`locales/models.py`), and runtime
  utilities (`locales/utils.py`)

### II. Runtime Configuration First

**Application behavior MUST be configurable via admin interface without code changes.**

- Core settings (languages, site configuration) MUST be editable via Wagtail admin
- Database-driven configuration takes precedence over code defaults
- Settings changes requiring restart MUST be clearly documented
- Graceful fallbacks MUST be provided when database is unavailable
- Rationale: Enables non-technical administrators to manage site configuration. Supports
  multi-tenant architecture where different sites need different settings.

### III. Security First (NON-NEGOTIABLE)

**Security vulnerabilities MUST be prevented by design, not by policy.**

- RawHTMLBlock MUST NEVER be used (XSS vulnerability)
- EmbedBlock (oEmbed) MUST be used for all embedded content
- User input MUST be sanitized at the framework level
- Security reviews MUST occur for any feature accepting external content
- Rationale: Protects Quaker communities from security threats. One vulnerability can
  compromise sensitive community data or meeting communications.

### IV. Test-Driven Development

**All features MUST have comprehensive tests organized by functionality.**

- Tests MUST be organized by feature: ModelTests, StreamFieldTests, TranslationTests,
  AdminTests, IntegrationTests
- Test names MUST clearly describe what is being tested
- Model changes MUST include tests for behavior and validation
- StreamField changes MUST include tests for block structure
- Rationale: Ensures reliability for communities depending on the system for important
  communications. Organized tests make codebase maintainable as features grow.

### V. Code Quality Standards

**Code quality MUST be automatically enforced, not manually reviewed.**

- Pre-commit hooks MUST run on all commits
- Ruff MUST be used for linting and formatting
- Pyupgrade MUST enforce Python 3.12+ syntax
- Django-upgrade MUST enforce Django 5.2+ patterns
- Template linting MUST use djhtml and curlylint
- All CI checks MUST pass before merge
- Rationale: Prevents technical debt. Automated enforcement scales better than manual review.
  Consistent code style improves collaboration.

### VI. Migration Discipline

**Database schema changes MUST be tracked, versioned, and reversible.**

- ALL model changes MUST generate migrations via `makemigrations`
- StreamField block structure changes MUST generate migrations
- Migration files MUST be committed to version control
- Migration tests MUST verify data integrity during schema changes
- Rationale: Enables safe deployments and rollbacks. Multiple environments (dev, staging,
  production) must stay synchronized. Lost or incorrect migrations cause data loss.

### VII. Internationalization First

**Global accessibility MUST be a first-class feature, not an afterthought.**

- 19+ languages MUST be supported out of the box
- Language configuration MUST be runtime-adjustable (via LocaleSettings)
- Content MUST be per-locale, not auto-translated
- Translation UI MUST be available for all page types
- Language codes MUST follow standard formats (en, es, fr, etc.)
- Rationale: Quaker communities exist worldwide. English-only systems exclude non-English
  speaking meetings. Runtime configuration allows communities to enable only the languages
  they need.

## Technology Stack Requirements

**Technology choices ensure long-term maintainability and community contribution.**

### Required Technologies

- **Python 3.12+**: Modern Python with latest features and security updates
- **Django 5.2+**: LTS framework with security support
- **Wagtail 7.0+**: Flexible CMS with excellent editing experience
- **uv**: Fast, reliable package management
- **SQLite** (dev) / **PostgreSQL** (production): Standard Django-compatible databases

### Prohibited Technologies

- Proprietary services or software (violates open source philosophy)
- Google-dependent mapping services (use open alternatives)
- Technologies requiring non-standard Python versions

### Standards Compliance

- RSS/Atom for content syndication
- Open web standards for all public-facing features
- Responsive design (mobile-friendly)
- WCAG accessibility guidelines

## Development Workflow

### Quality Gates (ALL required before merge)

1. **Pre-commit Hooks Pass**: Ruff linting/formatting, pyupgrade, django-upgrade, template
   linting
2. **Tests Pass**: All existing tests continue passing
3. **New Tests Added**: Features include appropriate tests (Model/StreamField/Translation/etc.)
4. **Migrations Generated**: Model changes include migration files
5. **CI Pipeline Passes**: GitHub Actions runs full test matrix (Python 3.12, 3.13)
6. **Documentation Updated**: AGENTS.md updated for architectural changes, README updated for
   user-facing changes

### Commit Requirements

- Descriptive commit messages following conventional commits style
- One logical change per commit
- No bypassing pre-commit hooks (no `--no-verify`)

### Review Process

- All changes via pull request (no direct commits to main)
- CI must pass before review
- At least one approving review required
- Reviewer verifies constitution compliance

## Governance

### Constitutional Authority

This constitution supersedes all other development practices and guidelines. When conflicts
arise between this document and other guidance:

1. Constitution takes precedence
2. AGENTS.md provides implementation details
3. Other documentation provides context

### Amendment Process

**MAJOR version bump** (backward incompatible):

- Removing or fundamentally changing a core principle
- Changing required technology stack
- Removing quality gates

**MINOR version bump** (backward compatible):

- Adding new principles
- Expanding existing principles with new requirements
- Adding new sections

**PATCH version bump** (clarifications):

- Fixing typos or unclear wording
- Adding examples or rationale
- Reorganizing without changing meaning

All amendments MUST:

- Be approved by project maintainers
- Include rationale for the change
- Update dependent documentation (AGENTS.md, templates, etc.)
- Be documented in this file's sync impact report

### Compliance Verification

- All pull requests MUST verify constitutional compliance
- Template files (.specify/templates/) MUST align with principles
- AGENTS.md MUST reflect current principles for AI agent guidance
- CI pipeline MUST enforce automated principles (code quality, tests, etc.)

### Runtime Development Guidance

For detailed implementation guidance that complements this constitution, see `AGENTS.md` in
the project root. That file provides:

- Specific code patterns and examples
- Common pitfalls and solutions
- Debugging tips
- Detailed workflow instructions

**Version**: 1.0.0 | **Ratified**: 2025-10-26 | **Last Amended**: 2025-10-26
