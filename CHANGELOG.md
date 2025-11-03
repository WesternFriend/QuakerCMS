# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Navigation Menu System**: Site-wide multi-lingual navigation with WCAG 2.1 AA accessibility
  - Site-wide navigation menu configuration via Wagtail Settings (BaseSiteSetting pattern)
  - StreamField-based menu structure with PageLinkBlock, ExternalLinkBlock, and DropdownMenuBlock
  - **2-level menu maximum**: Enforced at schema level - prevents nested dropdowns
  - **Locale-aware rendering**: Automatic page translation linking with fallback to default locale
  - **Full WCAG 2.1 AA compliance**: ARIA menubar pattern, keyboard navigation, screen reader support
  - **DaisyUI responsive design**: Mobile hamburger drawer, desktop horizontal menu
  - **Accessibility features**:
    - Skip link to main content (first focusable element)
    - ARIA attributes (role, aria-label, aria-current, aria-expanded, aria-haspopup, aria-controls)
    - 44x44px minimum touch targets for mobile
    - Visible focus indicators (3:1 contrast ratio)
    - Progressive enhancement with `<details>`/`<summary>` for dropdowns
  - **Dropdown edge detection**: JavaScript prevents viewport overflow (opens left/right/down based on space)
  - **Keyboard support**: Tab, Enter, Space, Escape, Arrow keys for full navigation
  - **Theme-aware**: Automatic adaptation to light/dark mode via DaisyUI
  - **7 comprehensive tests**: ModelTests, StreamFieldTests, IntegrationTests for dropdown structure
  - Developer documentation in `specs/002-nav-menu-system/` (plan, data model, contracts, quickstart)
  - Template tag: `{% load navigation_tags %}{% navigation_menu %}`
- **Tailwind CSS Integration**: Modern utility-first CSS framework with DaisyUI components
  - Tailwind CSS v4 with @source directive for automatic template scanning
  - DaisyUI plugin with semantic component classes (buttons, cards, navigation, forms, alerts)
  - @tailwindcss/typography plugin for professional prose styling
  - django-tailwind package for seamless Django integration
  - django-browser-reload for hot reloading in development
  - Dark mode support with automatic system preference detection
  - Production CSS bundle optimized to 9.54 KB gzipped (well under 50KB target)
  - **100% test pass rate**: 8 new tests for Tailwind integration, DaisyUI components, and dark mode
  - Developer documentation in `specs/001-tailwind-integration/quickstart.md`
- **Locales App**: Runtime language configuration system
  - `LocaleSettings` model for per-site language configuration via Wagtail admin
  - Support for 19+ languages including English, Spanish, French, German, Portuguese, Italian, Dutch, Scandinavian languages, Russian, Japanese, Chinese (Simplified/Traditional), Korean, Arabic, and Swahili
  - Management commands: `show_language_settings` and `sync_locales`
  - Automatic syncing between `LocaleSettings` and Wagtail's `Locale` model
  - Content protection: prevents deletion of locales with existing pages
  - Comprehensive test coverage (38 tests) for locale management
  - Detailed documentation in `src/locales/README.md`
- **Content App**: Flexible content page system with StreamField
  - `ContentPage` model with semantic StreamField blocks
  - `HeadingBlock`: Custom StructBlock for h2-h4 semantic headings (h1 reserved for page title)
  - Rich text, image, quote, and embed blocks
  - Safe `EmbedBlock` (oEmbed)
  - Hierarchical page structure (ContentPages can nest)
  - Full translation support for multi-locale content
  - Comprehensive test coverage (26 tests) including translation, StreamField, and admin tests
- **Centralized Constants**: `src/core/constants.py` for i18n configuration
  - Single source of truth for `DEFAULT_LANGUAGE_CODE`, `DEFAULT_LANGUAGES`, and `LANGUAGE_CHOICES`
  - Consistent usage across settings, models, and utilities
- **AI Coding Agent Instructions**: `.github/copilot-instructions.md` (replaces AGENTS.md)
  - Architecture patterns and critical conventions
  - Development workflow and commands
  - Common pitfalls and debugging tips
  - Test structure conventions
- **Wagtail Internationalization**: Full i18n support
  - `wagtail.contrib.simple_translation` for translation UI
  - `WAGTAIL_I18N_ENABLED = True` for content localization
  - Per-locale content management
- Initial project setup with Django and Wagtail CMS
- Basic content management for Quaker communities
- Pre-commit hooks for code quality
- GitHub Actions CI pipeline
- Test coverage reporting
- Security policy
- Issue and PR templates
- Automated dependency updates with Dependabot

### Changed

- **Norwegian Language Code**: Updated from `"no"` to `"nb"` (Norwegian Bokmål) for ISO 639-1 compliance
- **HomePage Model**: Updated to allow `ContentPage` as subpage type
- **Pre-commit Config**: Updated ruff version and added additional hooks
- **Settings Structure**: Enhanced internationalization configuration with centralized constants

### Security

- **XSS Prevention**: All content uses safe blocks (`EmbedBlock` with oEmbed protocol)
- **Content Protection**: Validation prevents accidental deletion of locales with existing content
- Added security policy and vulnerability reporting process

## [0.1.0] - 2025-07-02

### Added

- Initial release
- Basic Django/Wagtail project structure
- Home page and search functionality
- Development environment setup with uv
- Code quality tools (ruff, pre-commit)
- Contributing guidelines
- README with project vision and goals

[Unreleased]: https://github.com/WesternFriend/QuakerCMS/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/WesternFriend/QuakerCMS/releases/tag/v0.1.0
