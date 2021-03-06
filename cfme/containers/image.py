from cfme.common import Taggable
from cfme.fixtures import pytest_selenium as sel
from cfme.web_ui import toolbar as tb
from cfme.web_ui.menu import nav

from . import list_tbl, pol_btn

nav.add_branch(
    'containers_images',
    {
        'containers_image':
        [
            lambda ctx: list_tbl.select_row_by_cells(
                {'Name': ctx['image'].name, 'Provider': ctx['provider'].name}),
            {
                'containers_image_edit_tags':
                lambda _: pol_btn('Edit Tags'),
            }
        ],
        'containers_image_detail':
        [
            lambda ctx: list_tbl.click_row_by_cells(
                {'Name': ctx['image'].name, 'Provider': ctx['provider'].name}),
            {
                'containers_image_edit_tags_detail':
                lambda _: pol_btn('Edit Tags'),
            }
        ]
    }
)


class Image(Taggable):

    def __init__(self, name, provider):
        self.name = name
        self.provider = provider

    def load_details(self, refresh=False):
        if not self._on_detail_page():
            self.navigate(detail=True)
        elif refresh:
            tb.refresh()

    def navigate(self, detail=True):
        if detail is True:
            if not self._on_detail_page():
                sel.force_navigate('containers_image_detail',
                    context={'image': self, 'provider': self.provider})
        else:
            sel.force_navigate('containers_image',
                context={'image': self, 'provider': self.provider})
