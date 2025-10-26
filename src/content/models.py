from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class ContentPage(Page):
    """
    A general-purpose page model with a flexible StreamField body.
    """

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
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

    subpage_types = ["content.ContentPage"]
    parent_page_types = [
        "home.HomePage",
        "content.ContentPage",
    ]

    class Meta:
        verbose_name = "Content Page"
        verbose_name_plural = "Content Pages"
