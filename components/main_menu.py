from __future__ import print_function, unicode_literals

from django.contrib.auth import logout
from django.utils.translation import ugettext_lazy as _

from cba import components

from notes.components.note_edit import NoteEdit


class MainMenu(components.Menu):
    def init_components(self):
        self.initial_components = [
            components.MenuItem(name="Add", handler="handle_add_note"),
            components.MenuItem(name="Logout", handler="handle_logout"),
        ]

    def handle_about_us(self):
        root = self.get_root()
        root.add_component(
            components.Modal(
                header="About us",
                initial_components=[
                    components.HTML(
                        tag="span",
                        text="""Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.""")
                ]),
        )
        root.refresh()

    def handle_add_note(self):
        note_edit = NoteEdit(id="note-edit", css_class="container form")
        main = self.get_component("main")
        main.replace_component("note-view", note_edit)
        main.refresh()

    def handle_logout(self):
        request = self.get_request()
        logout(request)

        root = self.get_root()
        root.refresh_all()
        root.add_message(_("You are logged out!"), "success")
