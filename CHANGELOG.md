# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
