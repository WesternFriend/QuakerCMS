from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

from content.models import HeadingBlock


class HomePage(Page):
    template = "home/home_page.html"

    body = StreamField(
        [
            ("heading", HeadingBlock()),
            ("rich_text", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("quote", blocks.BlockQuoteBlock()),
            ("embed", EmbedBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    # Only allow one HomePage instance
    max_count = 1

    # Allow ContentPage as a child
    subpage_types = ["content.ContentPage"]
