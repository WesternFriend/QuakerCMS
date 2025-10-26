# Feature Specification: Tailwind CSS Integration

**Feature Branch**: `001-tailwind-integration`
**Created**: 2025-10-26
**Status**: Draft
**Input**: User description: "Add Tailwind CSS with DaisyUI and tailwindcss/typography for using prose over CMS content like RichText fields"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Content Styling with Typography (Priority: P1)

Content managers need to publish RichText content (articles, epistles, minutes, newsletters) that is visually appealing and readable without manually applying CSS classes to every element. The typography plugin should automatically style HTML content from the CMS with professional typographic defaults.

**Why this priority**: Core value proposition - makes CMS content immediately readable and professional-looking without additional work from content managers. This is essential for the primary use case of publishing Quaker community content.

**Independent Test**: Can be fully tested by creating a page with RichText content, viewing it on the frontend, and verifying that headings, paragraphs, lists, and blockquotes are automatically styled with appropriate typography. Delivers immediate value by making published content look professional.

**Acceptance Scenarios**:

1. **Given** a content manager creates a page with RichText content containing headings, paragraphs, and lists, **When** they save and view the page on the frontend, **Then** all text elements display with consistent, professional typography styling without requiring manual CSS classes
2. **Given** a published page contains block quotes and emphasis elements in RichText, **When** a site visitor views the page, **Then** block quotes are visually distinguished and emphasized text stands out appropriately
3. **Given** a RichText field contains links and code snippets, **When** rendered on the page, **Then** links are styled distinctly and code blocks have appropriate monospace formatting
4. **Given** a page is viewed on different screen sizes, **When** the viewport width changes, **Then** typography scales appropriately for readability on mobile, tablet, and desktop

---

### User Story 2 - Consistent UI Components (Priority: P2)

Site administrators and developers need to create custom templates and UI components (navigation, forms, cards, modals) that maintain a consistent design language across the site. DaisyUI components should provide pre-built, accessible patterns that work seamlessly with Wagtail's admin interface.

**Why this priority**: Enables creating a cohesive user interface without writing extensive custom CSS. Important for maintainability and consistency, but doesn't directly impact content publishing (the primary workflow).

**Independent Test**: Can be fully tested by creating a custom template using DaisyUI component classes (buttons, cards, navigation), viewing the result, and verifying components render with consistent styling and respond to user interactions. Delivers value by accelerating UI development.

**Acceptance Scenarios**:

1. **Given** a developer creates a navigation template using DaisyUI navbar classes, **When** the navigation is rendered, **Then** it displays with consistent styling, proper spacing, and responsive behavior
2. **Given** a form template uses DaisyUI form component classes, **When** users interact with form fields, **Then** inputs, buttons, and validation states follow consistent design patterns
3. **Given** templates use DaisyUI card and modal components, **When** content is displayed, **Then** cards maintain consistent layout and modals function with proper accessibility
4. **Given** multiple pages use different DaisyUI components, **When** navigating between pages, **Then** all components maintain visual consistency following the same design system

---

### User Story 3 - Dark Mode Support (Priority: P3)

Site visitors want the ability to view content in dark mode to reduce eye strain and match their system preferences. The typography styling should adapt seamlessly to dark backgrounds while maintaining readability.

**Why this priority**: Enhances user experience and accessibility but is not critical for core functionality. Can be added after basic styling is working.

**Independent Test**: Can be fully tested by toggling dark mode (either via system preference or site control) and verifying that prose content remains readable with appropriately inverted colors. Delivers value by improving comfort for users who prefer dark interfaces.

**Acceptance Scenarios**:

1. **Given** a visitor has dark mode enabled in their system preferences, **When** they view a page with prose content, **Then** text and background colors invert appropriately while maintaining contrast and readability
2. **Given** prose content contains code blocks and blockquotes in dark mode, **When** viewed, **Then** these elements are distinguishable with appropriate dark mode styling
3. **Given** a visitor toggles between light and dark mode, **When** the mode changes, **Then** the transition is smooth and all typography elements adapt without layout shifts

---

### Edge Cases

- What happens when RichText content contains custom HTML that conflicts with Tailwind's prose classes?
- How does the system handle very long words or URLs that might break layout on narrow screens?
- What happens when prose content is nested inside other styled containers?
- How does typography styling interact with Wagtail's admin preview mode versus published pages?
- What happens when DaisyUI theme colors conflict with existing custom CSS?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST integrate django-tailwind package to manage Tailwind CSS compilation and development workflow
- **FR-002**: System MUST install and configure Tailwind CSS v4 as the default version
- **FR-003**: System MUST include DaisyUI plugin for component library support
- **FR-004**: System MUST include @tailwindcss/typography plugin for prose styling
- **FR-005**: System MUST provide automatic page reload during development when templates or styles change
- **FR-006**: System MUST generate production-optimized CSS builds that remove unused styles (built manually and committed to repository)
- **FR-007**: RichText content MUST automatically receive prose styling without content managers manually adding classes
- **FR-008**: System MUST support dark mode via prose-invert class with proper color contrast
- **FR-009**: Tailwind styles MUST NOT interfere with Wagtail admin interface styling
- **FR-010**: System MUST scan Django templates, Python files, and JavaScript files for Tailwind class usage
- **FR-011**: Development server MUST support both Django runserver and Tailwind watcher running concurrently
- **FR-012**: System MUST provide template tags for including Tailwind CSS and preloading stylesheets
- **FR-013**: System MUST configure DaisyUI with a default light theme and a dark theme that activates based on system preference (prefers-color-scheme: dark)

### Key Entities

- **Theme App**: A Django app containing Tailwind configuration, source CSS files, and compiled output
- **Prose Content**: RichText field content that needs automatic typography styling
- **Style Configuration**: Tailwind configuration specifying source file paths, plugins, and theme customization
- **Development Watcher**: Background process that monitors files and recompiles CSS on changes

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Content managers can publish RichText content that appears professionally styled without manually applying any CSS classes
- **SC-002**: Page load time increases by less than 200ms compared to baseline (production CSS is optimized)
- **SC-003**: Development workflow supports live reload - changes to templates reflect in browser within 2 seconds
- **SC-004**: Typography styles maintain WCAG AA contrast ratios in both light and dark modes
- **SC-005**: Production CSS bundle size is under 50KB (gzipped) due to unused style purging
- **SC-006**: Developers can add new UI components using DaisyUI classes without writing custom CSS
- **SC-007**: All prose content displays readably on screens from 320px to 2560px wide

## Assumptions

- Django development environment is already set up with Python 3.12+
- Node.js and npm are available in the development environment (required by django-tailwind)
- Content managers publish content using Wagtail's RichText editor (StreamField with RichTextBlock)
- Production deployment uses pre-built CSS committed to repository (no build step required)
- Browser targets include modern browsers with CSS Grid and Custom Properties support (no IE11)
- Dark mode detection will use CSS media query `prefers-color-scheme: dark` as the default mechanism
- Existing templates use standard Django/Wagtail template structure that can be extended
- Development team is familiar with utility-first CSS frameworks (or willing to learn)

## Clarifications

### Session 2025-10-26

- Q: Should this feature include the ability to customize Tailwind/DaisyUI theme values (colors, fonts, spacing), or should it use only the default themes? → A: Use one of the default DaisyUI themes, specified for both dark and light variants (e.g., light --default, dark --prefersdark)
- Q: How should the deployment process handle Tailwind CSS build failures? → A: Build CSS manually and commit it to the repository - no deployment-time CSS compilation needed
