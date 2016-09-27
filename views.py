from __future__ import print_function, unicode_literals

from django.utils.translation import ugettext_lazy as _

from taggit.models import Tag
from cba import components
from cba.views import CBAView

from notes.models import Note
from notes.components.login import Login
from notes.components.main_menu import MainMenu
from notes.components.note_edit import NoteEdit
from notes.components.note_view import NoteView


class NotesRoot(components.Group):
    def init_components(self):
        if self.get_request().user.is_anonymous():
            self.initial_components = [
                Login(id="login-form"),
            ]
        else:
            self.initial_components = [
                MainMenu(id="menu", css_class="large inverted"),
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
            ]


class NotesView(CBAView):
    root = NotesRoot
