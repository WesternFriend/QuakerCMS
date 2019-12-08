from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField



class HomePage(Page):
    body = RichTextField(null=True, blank=True)

    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]
