from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

# Non-translatable URLs
# These URLs will not have a language prefix
urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Browser reload for Tailwind CSS development
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]

# Translatable URLs
# Wagtail's i18n support requires i18n_patterns to add language prefixes to URLs.
# With prefix_default_language=False, English pages won't have /en/ prefix.
urlpatterns += i18n_patterns(
    path("search/", search_views.search, name="search"),
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)
