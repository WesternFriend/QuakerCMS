# Tasks: Tailwind CSS Integration

**Feature Branch**: `001-tailwind-integration`
**Input**: Design documents from `/specs/001-tailwind-integration/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, quickstart.md ✅

**Tests**: Included per constitution requirement IV (Test-Driven Development)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install django-tailwind package and create theme app structure

- [x] T001 Install django-tailwind package with reload extras using `uv add django-tailwind[reload]`
- [x] T002 Add 'tailwind' to INSTALLED_APPS in src/core/settings/base.py
- [x] T003 Initialize theme app using `python manage.py tailwind init` (accept default name 'theme')
- [x] T004 Add 'theme' to INSTALLED_APPS in src/core/settings/base.py
- [x] T005 Add TAILWIND_APP_NAME = 'theme' configuration to src/core/settings/base.py
- [x] T006 Install Tailwind CSS dependencies using `python manage.py tailwind install`
- [x] T007 Update .gitignore to exclude node_modules/ and src/theme/static/css/dist/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configure development environment and install Tailwind plugins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Add 'django_browser_reload' to INSTALLED_APPS in src/core/settings/dev.py (within DEBUG check)
- [x] T009 Add BrowserReloadMiddleware to MIDDLEWARE in src/core/settings/dev.py (within DEBUG check)
- [x] T010 Add browser reload URL pattern to src/core/urls.py (within DEBUG check)
- [x] T011 Install DaisyUI plugin using `python manage.py tailwind plugin_install daisyui`
- [x] T012 Install typography plugin using `python manage.py tailwind plugin_install @tailwindcss/typography`
- [x] T013 Configure DaisyUI themes in src/theme/static_src/src/styles.css (light default, dark via prefers-color-scheme)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Content Styling with Typography (Priority: P1) 🎯 MVP

**Goal**: Enable content managers to publish RichText content with professional typography automatically applied

**Independent Test**: Create a page with RichText content containing headings, paragraphs, lists, and links, then verify all elements display with consistent professional styling without manual CSS classes

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US1] Create test for template rendering with Tailwind stylesheet tags in src/content/tests.py
- [x] T015 [P] [US1] Create test for prose class application to RichText content in src/content/tests.py
- [x] T016 [P] [US1] Create test for CSS file generation in development mode in src/content/tests.py

### Implementation for User Story 1

- [x] T017 [US1] Create or update base template with tailwind_preload_css and tailwind_css tags in src/core/templates/base.html
- [x] T018 [P] [US1] Update ContentPage template to wrap body with prose classes in src/content/templates/content/content_page.html
- [x] T019 [P] [US1] Update HomePage template to wrap body with prose classes in src/home/templates/home/home_page.html
- [x] T020 [US1] Verify development server starts with `python manage.py tailwind dev` command
- [x] T021 [US1] Verify browser reload works when templates change
- [x] T022 [US1] Verify all User Story 1 tests pass

**Checkpoint**: At this point, User Story 1 should be fully functional - content managers can publish styled content

---

## Phase 4: User Story 2 - Consistent UI Components (Priority: P2)

**Goal**: Enable developers to create custom templates using DaisyUI component classes for consistent design

**Independent Test**: Create a template using DaisyUI component classes (buttons, cards, navigation) and verify components render with consistent styling

### Tests for User Story 2

- [x] T023 [P] [US2] Create test for DaisyUI button component rendering in src/content/tests.py
- [x] T024 [P] [US2] Create test for DaisyUI card component rendering in src/content/tests.py

### Implementation for User Story 2

- [x] T025 [P] [US2] Create example navigation component using DaisyUI navbar classes in src/core/templates/components/navigation.html
- [x] T026 [P] [US2] Document DaisyUI component usage patterns in specs/001-tailwind-integration/quickstart.md
- [x] T027 [US2] Verify DaisyUI components render correctly in development server
- [x] T028 [US2] Verify all User Story 2 tests pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Dark Mode Support (Priority: P3)

**Goal**: Enable site visitors to view content in dark mode based on system preferences

**Independent Test**: Toggle dark mode in system preferences and verify prose content inverts colors while maintaining readability

### Tests for User Story 3

- [x] T029 [P] [US3] Create test for prose-invert class application in dark mode in src/content/tests.py
- [x] T030 [P] [US3] Create test for DaisyUI dark theme activation in src/content/tests.py

### Implementation for User Story 3

- [x] T031 [P] [US3] Add dark:prose-invert class to ContentPage template in src/content/templates/content/content_page.html
- [x] T032 [P] [US3] Add dark:prose-invert class to HomePage template in src/home/templates/home/home_page.html
- [x] T033 [US3] Verify dark mode theme configuration in src/theme/static_src/src/styles.css
- [x] T034 [US3] Test dark mode switching with system preference toggle
- [x] T035 [US3] Verify all User Story 3 tests pass

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Production optimization and documentation

- [x] T036 [P] Build production CSS bundle using `python manage.py tailwind build`
- [x] T037 [P] Verify production CSS bundle size is under 50KB gzipped (Success Criteria SC-005)
- [x] T038 [P] Verify page load time impact is under 200ms (Success Criteria SC-006)
- [x] T039 [P] Verify WCAG AA contrast ratios for all DaisyUI themes (Success Criteria SC-008)
- [x] T040 [P] Verify responsive behavior across 320px-2560px (Success Criteria SC-009)
- [x] T041 [S] Update CHANGELOG.md with integration details
- [x] T042 [S] Run full test suite and verify all tests pass
- [x] T043 [S] Validate implementation against quickstart.md documentation

**Final Checkpoint**: Implementation complete, all success criteria met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1 templates but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Template updates before verification
- All story tests must pass before checkpoint

### Parallel Opportunities

- **Phase 1**: T001-T007 are sequential (each depends on previous)
- **Phase 2**: T008-T010 (dev config) can run parallel to T011-T012 (plugin install)
- **Phase 3 Tests**: T014, T015, T016 can run in parallel (different test cases)
- **Phase 3 Implementation**: T018 and T019 can run in parallel (different template files)
- **Phase 4 Tests**: T023 and T024 can run in parallel (different test cases)
- **Phase 4 Implementation**: T025 and T026 can run in parallel (different files)
- **Phase 5 Tests**: T029 and T030 can run in parallel (different test cases)
- **Phase 5 Implementation**: T031 and T032 can run in parallel (different template files)
- **Phase 6**: T036-T040 can all run in parallel (different validation activities)

---

## Parallel Execution Examples

### Phase 2 Foundational (can split into two parallel tracks)

```bash
# Track A: Development configuration
T008: Add django_browser_reload to INSTALLED_APPS
T009: Add BrowserReloadMiddleware to MIDDLEWARE
T010: Add browser reload URL pattern

# Track B: Plugin installation
T011: Install DaisyUI plugin
T012: Install typography plugin
T013: Configure DaisyUI themes
```

### Phase 3 User Story 1 (tests and templates in parallel)

```bash
# All tests can run together:
T014: Template rendering test
T015: Prose class application test
T016: CSS generation test

# Template updates can run together:
T018: Update ContentPage template
T019: Update HomePage template
```

### Phase 6 Polish (all validation tasks in parallel)

```bash
# All verification tasks can run together:
T036: Build production CSS
T037: Verify bundle size
T038: Verify page load time
T039: Verify contrast ratios
T040: Verify responsive behavior
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T013) - CRITICAL
3. Complete Phase 3: User Story 1 (T014-T022)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Polish and optimize → Final production release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T013)
2. Once Foundational is done (checkpoint reached):
   - **Developer A**: User Story 1 (T014-T022) - Typography
   - **Developer B**: User Story 2 (T023-T028) - DaisyUI Components
   - **Developer C**: User Story 3 (T029-T035) - Dark Mode
3. Stories complete and integrate independently
4. Team collaborates on Phase 6 Polish (T036-T043)

---

## Constitution Compliance

This task list ensures compliance with QuakerCMS Constitution v1.0.0:

- ✅ **I. Centralized Constants**: DaisyUI theme config in styles.css, not scattered
- ✅ **II. Runtime Configuration**: CSS classes applied in templates (runtime-editable)
- ✅ **III. Security First**: No RawHTMLBlock usage, prose classes on sanitized content
- ✅ **IV. Test-Driven Development**: Tests included for each user story (T014-T016, T023-T024, T029-T030)
- ✅ **V. Code Quality Standards**: Changes follow existing pre-commit hooks (ruff, djhtml, curlylint)
- ✅ **VI. Migration Discipline**: N/A - no model changes
- ✅ **VII. Internationalization First**: Tailwind is language-agnostic, supports all locales

---

## Notes

- [P] tasks = different files, no dependencies between them
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Tests are written BEFORE implementation (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Development server command: `python manage.py tailwind dev`
- Production build command: `python manage.py tailwind build`
