from __future__ import print_function, unicode_literals

from django.utils.translation import ugettext_lazy as _

from cba import components
from cba import layouts
from cba.views import CBAView

from notes.components.login import Login
from notes.components.main_menu import MainMenu
from notes.components.note_view import NoteView
from notes.components.tag_explorer import TagExplorer


class NotesRoot(components.Group):
    def init_components(self):
        if self.get_request().user.is_anonymous():
            self.initial_components = [
                Login(id="login-form"),
            ]
        else:
            self.initial_components = [
                MainMenu(id="menu", css_class="large inverted"),
                layouts.Grid(
                    initial_components=[
                        layouts.Column(
                            width=13,
                            initial_components=[
                                components.Group(
                                    id="main",
                                    css_class="ui container",
                                    initial_components=[
                                        NoteView(
                                            id="note-view",
                                            attributes={"style": "padding-top: 10px"},
                                        )
                                    ],
                                ),
                            ],
                        ),
                        layouts.Column(
                            width=3,
                            initial_components=[
                                components.HTML(text=_("Tag Explorer"), tag="div", css_class="ui sub header", attributes={"style": "padding: 10px 0"}),
                                TagExplorer(id="tag-explorer"),
                            ],
                        ),
                    ]
                ),
            ]


class NotesView(CBAView):
    root = NotesRoot
