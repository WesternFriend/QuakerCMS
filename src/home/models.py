from wagtail.models import Page


class HomePage(Page):
    template = "home/home_page.html"

    # Only allow one HomePage instance
    max_count = 1
