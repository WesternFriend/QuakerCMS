# Quickstart: Tailwind CSS Integration

**Feature**: Tailwind CSS Integration
**Last Updated**: 2025-10-26
**Prerequisites**: Python 3.12+, Node.js 18+, npm 9+

## Quick Start Guide

This guide will get you up and running with Tailwind CSS, DaisyUI, and Typography plugin in QuakerCMS.

### Installation (5 minutes)

1. **Install django-tailwind package**

   ```bash
   cd /path/to/QuakerCMS
   uv add django-tailwind[reload]
   ```

2. **Add to INSTALLED_APPS** (`src/core/settings/base.py`)

   ```python
   INSTALLED_APPS = [
       # ... existing apps ...
       'tailwind',
   ]
   ```

3. **Create theme app**

   ```bash
   cd src
   python manage.py tailwind init
   ```

   When prompted, accept default app name: `theme`

4. **Add theme app to settings** (`src/core/settings/base.py`)

   ```python
   INSTALLED_APPS = [
       # ... existing apps ...
       'tailwind',
       'theme',  # Add this line
   ]

   # Add at bottom of file
   TAILWIND_APP_NAME = 'theme'
   ```

5. **Configure development mode** (`src/core/settings/dev.py`)

   ```python
   if DEBUG:
       INSTALLED_APPS += ['django_browser_reload']

   if DEBUG:
       MIDDLEWARE += [
           'django_browser_reload.middleware.BrowserReloadMiddleware',
       ]
   ```

6. **Add browser reload URLs** (`src/core/urls.py`)

   ```python
   from django.conf import settings

   # At bottom of file
   if settings.DEBUG:
       urlpatterns += [
           path("__reload__/", include("django_browser_reload.urls")),
       ]
   ```

7. **Install Tailwind dependencies**

   ```bash
   python manage.py tailwind install
   ```

8. **Install plugins**

   ```bash
   python manage.py tailwind plugin_install daisyui
   python manage.py tailwind plugin_install @tailwindcss/typography
   ```

### Development Workflow

**Start development server** (runs both Django and Tailwind watcher):

```bash
cd src
python manage.py tailwind dev
```

This command:
- Starts Django development server on http://127.0.0.1:8000
- Starts Tailwind watcher for live CSS recompilation
- Enables browser auto-reload on template/CSS changes

**Stop server**: Press `CTRL + C`

### Using Tailwind in Templates

1. **Update base template** (`src/core/templates/base.html` or create `src/theme/templates/base.html`)

   ```django
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
   ```

2. **Apply prose classes to RichText content**

   Edit page templates (e.g., `src/content/templates/content/content_page.html`):

   ```django
   {% extends "base.html" %}

   {% block content %}
       <article class="prose lg:prose-xl dark:prose-invert max-w-none">
           {{ page.body }}
       </article>
   {% endblock %}
   ```

3. **Use DaisyUI components**

   Example navigation with DaisyUI:

   ```django
   <div class="navbar bg-base-100">
       <div class="navbar-start">
           <a class="btn btn-ghost text-xl">QuakerCMS</a>
       </div>
       <div class="navbar-end">
           <a class="btn btn-primary">Get Started</a>
       </div>
   </div>
   ```

## Dark Mode Support

QuakerCMS includes automatic dark mode support that responds to the user's system preferences.

### Typography Dark Mode

All prose content automatically adapts to dark mode using the `dark:prose-invert` class:

```django
<article class="prose lg:prose-xl dark:prose-invert max-w-none">
  {{ page.body }}
</article>
```

This is already applied to `ContentPage` and `HomePage` templates.

### DaisyUI Dark Mode

DaisyUI components automatically switch between light and dark themes. Configuration in `src/theme/static_src/src/styles.css`:

```css
@plugin "daisyui" {
  themes: ["light", "dark"];
  darkTheme: "dark";
}
```

### Testing Dark Mode

**Chrome/Edge DevTools**:
1. Open DevTools (F12)
2. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
3. Type "Rendering"
4. Select "Emulate CSS media feature prefers-color-scheme: dark"

**System Settings**:
- **macOS**: System Settings → Appearance → Dark
- **Windows**: Settings → Personalization → Colors → Dark
- **Linux**: Desktop environment appearance settings

### Production Build

When deploying to production:

```bash
cd src
python manage.py tailwind build
python manage.py collectstatic --noinput
```

This creates an optimized CSS bundle (~50KB gzipped) in `theme/static/css/dist/styles.css`.

### Common Patterns

#### Using DaisyUI Components

DaisyUI provides semantic component classes that work alongside Tailwind utilities:

**Buttons**:
```django
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>
<button class="btn btn-ghost">Ghost Button</button>
<button class="btn btn-sm">Small Button</button>
<button class="btn btn-lg">Large Button</button>
```

**Cards**:
```django
<div class="card bg-base-100 shadow-xl">
    <div class="card-body">
        <h2 class="card-title">Card Title</h2>
        <p>Card content goes here.</p>
        <div class="card-actions justify-end">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
</div>
```

**Navigation** (see `src/core/templates/components/navigation.html` for full example):
```django
{% include "components/navigation.html" %}
```

**Forms**:
```django
<div class="form-control w-full max-w-xs">
    <label class="label">
        <span class="label-text">Email</span>
    </label>
    <input type="email" placeholder="you@example.com" class="input input-bordered w-full max-w-xs" />
</div>
```

**Alerts**:
```django
<div class="alert alert-info">
    <span>New updates available!</span>
</div>
```

For more DaisyUI components, see: https://daisyui.com/components/

#### Responsive Typography

```django
{# Small on mobile, large on desktop #}
<article class="prose prose-sm md:prose-base lg:prose-lg xl:prose-xl">
    {{ content }}
</article>
```

#### Dark Mode

```django
{# Automatically switches based on system preference #}
<article class="prose dark:prose-invert">
    {{ content }}
</article>
```

#### Constrained Width Content

```django
{# Centers content with max width #}
<div class="container mx-auto px-4">
    <article class="prose lg:prose-xl mx-auto">
        {{ page.body }}
    </article>
</div>
```

#### Full-Width Content

```django
{# No max-width constraint #}
<article class="prose lg:prose-xl max-w-none">
    {{ page.body }}
</article>
```

### Verification

1. **Check Tailwind is working**:
   - Start dev server: `python manage.py tailwind dev`
   - Visit http://127.0.0.1:8000
   - Inspect page source - should see `<link>` tag to `/static/css/dist/styles.css`
   - Check browser console - no CSS loading errors

2. **Check prose styling**:
   - Create a ContentPage with RichText content
   - Add headings, paragraphs, lists, and links
   - View page - content should have professional typography
   - Text should be readable with appropriate spacing

3. **Check DaisyUI**:
   - Add a button with `class="btn btn-primary"`
   - Button should have rounded corners, padding, and color
   - Hover should show interaction feedback

4. **Check dark mode**:
   - Enable dark mode in OS settings
   - Refresh page
   - Text should invert to light on dark background
   - Contrast should remain readable

### Troubleshooting

**CSS not loading?**
- Check that `{% tailwind_css %}` is in template `<head>`
- Verify Tailwind watcher is running (should see terminal output)
- Check browser console for 404 errors

**Styles not updating?**
- Ensure you're using `python manage.py tailwind dev` (not just `runserver`)
- Check that changed files match `@source` directive paths
- Try hard refresh in browser (Cmd+Shift+R / Ctrl+Shift+R)

**Node.js errors?**
- Verify Node.js 18+ installed: `node --version`
- Verify npm installed: `npm --version`
- Try removing `theme/node_modules/` and run `python manage.py tailwind install` again

**Plugins not working?**
- Check `theme/static_src/src/styles.css` has `@plugin` directives
- Verify plugins installed in `theme/package.json`
- Restart dev server after installing plugins

### Next Steps

- Read [Tailwind CSS documentation](https://tailwindcss.com/docs)
- Browse [DaisyUI components](https://daisyui.com/components/)
- Explore [Typography plugin options](https://tailwindcss.com/docs/typography-plugin)
- Customize theme colors in `theme/static_src/src/styles.css`
- Add custom utilities as needed

### Performance Tips

- Use responsive modifiers strategically (don't over-specify)
- Leverage `max-w-none` for full-width prose instead of custom CSS
- Monitor bundle size with `python manage.py tailwind build` in development
- Test production build before deploying: bundle should be <100KB uncompressed

### Development Best Practices

1. **Keep Tailwind classes in templates** - Don't extract to CSS files unless absolutely necessary
2. **Use DaisyUI semantic classes** - Prefer `btn` over manually combining utilities
3. **Test dark mode regularly** - Toggle OS setting and verify readability
4. **Restart server after plugin changes** - New plugins require process restart
5. **Commit theme/package.json and package-lock.json** - Ensures consistent dependencies

## Reference

**Management Commands**:
- `python manage.py tailwind init` - Create theme app
- `python manage.py tailwind install` - Install Node dependencies
- `python manage.py tailwind dev` - Start dev server (Django + Tailwind)
- `python manage.py tailwind start` - Start Tailwind watcher only
- `python manage.py tailwind build` - Build production CSS
- `python manage.py tailwind plugin_install <name>` - Install Tailwind plugin

**Template Tags**:
- `{% tailwind_css %}` - Include Tailwind stylesheet
- `{% tailwind_preload_css %}` - Preload stylesheet (performance)

**Key Files**:
- `theme/static_src/src/styles.css` - Source Tailwind file
- `theme/static/css/dist/styles.css` - Compiled output
- `theme/package.json` - Node dependencies
- `Procfile.tailwind` - Dev server process configuration

**Prose Classes**:
- `prose` - Base typography styling
- `prose-sm` / `prose-lg` / `prose-xl` - Size variants
- `prose-invert` - Dark mode styling
- `max-w-none` - Remove max-width constraint

**DaisyUI Classes**:
- Components: `btn`, `card`, `navbar`, `modal`, `drawer`, `hero`
- Modifiers: `btn-primary`, `btn-secondary`, `btn-ghost`, `btn-sm`, `btn-lg`
- See full list: https://daisyui.com/components/
