from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class HeadingBlock(blocks.StructBlock):
    """
    A custom heading block that allows users to select semantic heading levels.

    This encourages proper document structure and improves accessibility.

    Heading levels are restricted to h2-h4 because:
    - h1 is reserved for the page title
    - h2-h4 provide sufficient hierarchy for most content
    - Encourages shallow, accessible content structure
    """

    text = blocks.CharBlock(
        required=True,
        help_text="The heading text",
    )
    level = blocks.ChoiceBlock(
        choices=[
            ("h2", "Heading 2"),
            ("h3", "Heading 3"),
            ("h4", "Heading 4"),
        ],
        default="h2",
        help_text="Select the appropriate heading level for document hierarchy",
    )

    class Meta:
        icon = "title"
        template = "content/blocks/heading_block.html"


class ContentPage(Page):
    """
    A general-purpose page model with a flexible StreamField body.
    """

    body = StreamField(
        [
            ("heading", HeadingBlock()),
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
