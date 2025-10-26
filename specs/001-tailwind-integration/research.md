# Research: Tailwind CSS Integration

**Feature**: Tailwind CSS Integration
**Date**: 2025-10-26
**Phase**: 0 - Research & Technology Decisions

## Overview

This document consolidates research findings for integrating Tailwind CSS v4 with DaisyUI and Typography plugins into the QuakerCMS Django/Wagtail project.

## Technology Decisions

### 1. Django-Tailwind Package

**Decision**: Use `django-tailwind` package as the integration layer

**Rationale**:
- Official Django integration maintained by the community
- Handles Node.js/npm dependency management within Django project
- Provides management commands for initialization, development, and production builds
- Includes django-browser-reload for live reload during development
- Supports Tailwind CSS v4 with `--tailwind-version` flag (or v3 if needed)
- Manages separate theme app structure following Django conventions

**Alternatives Considered**:
- **Manual Tailwind CLI integration**: Rejected because it requires manual npm setup, custom build scripts, and doesn't integrate with Django's static file system as cleanly
- **django-compressor with Tailwind**: Rejected because django-compressor is designed for combining/minifying existing assets, not compiling Tailwind's utility-first approach
- **Webpack/Vite integration**: Rejected as overkill for a CSS-only requirement; adds JavaScript build complexity when we only need CSS compilation

**Implementation Notes**:
- Install with `pip install 'django-tailwind[reload]'` to include browser reload support
- Creates a dedicated Django app (named `theme` by convention) to house Tailwind configuration
- Version 4.0+ recommended as it uses the new `@source` directive instead of `content` configuration

### 2. Tailwind CSS Version

**Decision**: Use Tailwind CSS v4 (latest)

**Rationale**:
- Latest features including improved performance and smaller bundle sizes
- New `@source` directive simplifies content configuration (replaces v3's `content` array in config file)
- Better tree-shaking and unused style purging
- django-tailwind v4.0+ supports both v3 and v4 via `--tailwind-version` flag

**Alternatives Considered**:
- **Tailwind CSS v3**: Rejected because v4 offers performance improvements and is the recommended version for new projects. Migration path exists if needed.

**Implementation Notes**:
- Initialize with: `python manage.py tailwind init` (defaults to v4)
- Use `@source "../../**/*.{html,py,js}";` directive in `styles.css` to scan for class usage
- Adjust source paths based on actual project structure (Django apps at `src/*/`)

### 3. DaisyUI Component Library

**Decision**: Install DaisyUI as a Tailwind plugin

**Rationale**:
- Provides semantic component classes (btn, card, modal, navbar) reducing custom CSS
- Accessibility built-in with proper ARIA attributes
- Multiple theme support for potential future dark/light mode variants
- Works with existing Tailwind utilities without conflicts
- Small bundle size impact (~20KB) when tree-shaken

**Alternatives Considered**:
- **Custom component CSS**: Rejected because it requires significant development time and maintenance
- **Tailwind UI**: Rejected because it's a paid product with HTML components, not a plugin
- **Headless UI**: Rejected because it's React/Vue-focused, not suitable for Django templates

**Implementation Notes**:
- Install with: `python manage.py tailwind plugin_install daisyui`
- This automatically adds `@plugin "daisyui";` directive to `styles.css`
- Default theme is sufficient; custom themes can be configured later if needed

### 4. Typography Plugin

**Decision**: Install `@tailwindcss/typography` for prose styling

**Rationale**:
- Purpose-built for styling long-form content (exactly our use case with RichText fields)
- Provides `.prose` class with sensible defaults for headings, paragraphs, lists, blockquotes
- Responsive typography with `.prose-sm`, `.prose-lg`, `.prose-xl` modifiers
- Dark mode support via `.prose-invert` class
- Maintains proper typographic rhythm and spacing

**Alternatives Considered**:
- **Custom typography CSS**: Rejected because recreating professional typographic defaults is time-consuming and error-prone
- **Tiptap's styling**: Rejected because Tiptap is a different editor; we're using Wagtail's RichText
- **No styling (browser defaults)**: Rejected because browser defaults are inconsistent and unprofessional

**Implementation Notes**:
- Install with: `python manage.py tailwind plugin_install @tailwindcss/typography`
- Apply to RichText blocks: `<div class="prose lg:prose-xl">{{ page.body }}</div>`
- Dark mode: `<div class="prose dark:prose-invert">{{ page.body }}</div>`

### 5. Development Workflow

**Decision**: Use `python manage.py tailwind dev` for combined Django + Tailwind development server

**Rationale**:
- Single command starts both Django runserver and Tailwind watcher
- Uses Honcho to manage multiple processes via `Procfile.tailwind`
- django-browser-reload automatically refreshes browser on template/CSS changes
- Consistent with Django development workflow (no separate terminal needed)

**Alternatives Considered**:
- **Separate terminals**: Rejected because it's less convenient and error-prone (forgetting to start one server)
- **npm scripts**: Rejected because it moves control outside Django management commands
- **Custom shell script**: Rejected because Honcho is more robust and cross-platform

**Implementation Notes**:
- `Procfile.tailwind` created automatically on first run
- Contains: `django: python manage.py runserver` and `tailwind: python manage.py tailwind start`
- Can customize ports/addresses in Procfile if needed

### 6. Production Build Strategy

**Decision**: Run `python manage.py tailwind build` during deployment

**Rationale**:
- Generates optimized, minified CSS with unused styles purged
- Output goes to `theme/static/css/dist/styles.css` for Django's collectstatic
- Standard Django static file handling (no special CDN configuration needed)
- Significantly smaller bundle size (~50KB vs ~3MB development build)

**Alternatives Considered**:
- **Build in CI/CD**: Considered but adds complexity; better to keep build in deployment process
- **Pre-built CSS in repo**: Rejected because it bloats the repository and makes tracking changes difficult
- **CDN-hosted Tailwind**: Rejected because it doesn't support custom plugins or purging

**Implementation Notes**:
- Add to deployment script: `python manage.py tailwind build && python manage.py collectstatic --noinput`
- Ensure Node.js/npm available in production environment (or build in CI and copy static files)

### 7. Template Integration Strategy

**Decision**: Wrap RichText content with prose classes in page templates

**Rationale**:
- Non-invasive approach - doesn't modify CMS content or database
- Content managers don't need to know about CSS classes
- Consistent styling across all RichText blocks
- Easy to override or customize per-template if needed

**Alternatives Considered**:
- **Modify RichText output**: Rejected because it's fragile and breaks when Wagtail updates
- **Custom StreamField block**: Rejected as unnecessary; we just need a CSS class wrapper
- **JavaScript injection**: Rejected because it causes flash of unstyled content (FOUC)

**Implementation Notes**:
```django
{% load tailwind_tags %}
<!DOCTYPE html>
<html>
<head>
    {% tailwind_preload_css %}
    {% tailwind_css %}
</head>
<body>
    <article class="prose lg:prose-xl dark:prose-invert max-w-none">
        {{ page.body }}
    </article>
</body>
</html>
```

### 8. Wagtail Admin Isolation

**Decision**: Scope Tailwind styles to frontend only, exclude Wagtail admin

**Rationale**:
- Wagtail admin has its own styling that should not be affected
- Tailwind's utility classes could conflict with admin component styling
- Admin templates don't need prose styling

**Alternatives Considered**:
- **Prefix all Tailwind classes**: Rejected because it defeats the purpose of utility-first CSS
- **Separate stylesheets**: Considered but unnecessary since admin uses different templates

**Implementation Notes**:
- `@source` directive already scoped to `src/**/*.html` (doesn't include Wagtail admin templates)
- Admin templates are in virtualenv, not scanned by Tailwind
- Frontend templates explicitly load `{% tailwind_css %}`, admin templates don't

### 9. Dark Mode Implementation

**Decision**: Use CSS media query `prefers-color-scheme: dark` with prose-invert class

**Rationale**:
- Respects user's system preferences automatically
- No JavaScript required
- Standard approach for modern web applications
- Tailwind has built-in support via `dark:` variant

**Alternatives Considered**:
- **Manual toggle**: Considered for future enhancement but not MVP requirement
- **LocalStorage preference**: Considered for future enhancement
- **No dark mode**: Rejected because it's a P3 user story with clear value

**Implementation Notes**:
```django
<article class="prose dark:prose-invert">
    {{ page.body }}
</article>
```
- Tailwind automatically applies dark mode styles when `@media (prefers-color-scheme: dark)` matches
- Can add manual toggle in future by using `class` strategy: `darkMode: 'class'` in Tailwind config

## Best Practices Research

### Tailwind CSS with Django/Wagtail

**Finding**: Keep source files in `static_src/` and compiled output in `static/`

**Source**: django-tailwind documentation and Django static files best practices

**Implementation**:
- Source: `theme/static_src/src/styles.css`
- Output: `theme/static/css/dist/styles.css`
- Django's `collectstatic` picks up `theme/static/` automatically

### Performance Optimization

**Finding**: Use JIT (Just-In-Time) mode for fastest development builds

**Source**: Tailwind CSS v4 documentation - JIT is default in v4

**Implementation**:
- v4 enables JIT by default
- Development builds compile only used classes
- Production builds are fully optimized and purged

### Content Scanning Patterns

**Finding**: Include all file types that might contain Tailwind classes

**Source**: Tailwind CSS content configuration documentation

**Implementation**:
```css
@source "../../**/*.{html,py,js}";
```
- `html`: Django templates
- `py`: Python files (in case classes are in model methods or template tags)
- `js`: JavaScript files (for dynamic class manipulation)

### Responsive Design

**Finding**: Use Tailwind's responsive modifiers with mobile-first approach

**Source**: Tailwind CSS responsive design documentation

**Implementation**:
```html
<article class="prose lg:prose-xl">
  <!-- Mobile: base prose size -->
  <!-- Desktop (lg+): larger prose size -->
</article>
```

## Integration Patterns

### Django Settings Configuration

**Pattern**: Add django-tailwind apps to INSTALLED_APPS, configure in dev.py for development features

**Implementation**:
```python
# base.py
INSTALLED_APPS = [
    # ... existing apps
    'tailwind',
    'theme',  # generated by tailwind init
]

TAILWIND_APP_NAME = 'theme'

# dev.py
if DEBUG:
    INSTALLED_APPS += ['django_browser_reload']
    MIDDLEWARE += ['django_browser_reload.middleware.BrowserReloadMiddleware']
```

### URL Configuration

**Pattern**: Include browser reload URLs only in development

**Implementation**:
```python
# urls.py
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
```

### Template Inheritance

**Pattern**: Create a base template with Tailwind tags, extend in page templates

**Implementation**:
```django
{# theme/templates/base.html #}
{% load static tailwind_tags %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}QuakerCMS{% endblock %}</title>
    {% tailwind_preload_css %}
    {% tailwind_css %}
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

{# content/templates/content/content_page.html #}
{% extends "base.html" %}
{% block content %}
    <article class="prose lg:prose-xl dark:prose-invert max-w-none">
        {{ page.body }}
    </article>
{% endblock %}
```

## Risk Mitigation

### Node.js Dependency

**Risk**: Production deployment might not have Node.js installed

**Mitigation**:
- Option 1: Install Node.js in production environment (recommended for Tailwind v4)
- Option 2: Build CSS in CI/CD and commit to repository
- Option 3: Build CSS in Docker image during build step

### Bundle Size

**Risk**: Tailwind CSS bundle could be large if purging doesn't work correctly

**Mitigation**:
- Test production build and measure actual size
- Verify `@source` directive scans correct paths
- Monitor bundle size in CI/CD

### Breaking Changes

**Risk**: Tailwind CSS or plugins update with breaking changes

**Mitigation**:
- Pin versions in `package.json` (django-tailwind does this automatically)
- Test updates in development before deploying
- Review CHANGELOG before updating

## Conclusion

All technology decisions are finalized with clear rationales. No remaining unknowns block implementation. The research phase is complete, and we can proceed to Phase 1 (design and contracts).
