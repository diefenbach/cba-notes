from __future__ import print_function, unicode_literals

from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.utils.translation import ugettext_lazy as _

from cba import components, layouts
from cba.views import CBAView
from cba import get_request

from . models import Note


class Login(components.Group):
    def init_components(self):
        self.initial_components = [
            layouts.Grid(
                id="login-form",
                css_class="middle aligned center aligned",
                initial_components=[
                    layouts.Column(
                        initial_components=[
                            components.TextInput(
                                id="username",
                                label=_("Username")
                            ),
                            components.TextInput(
                                id="password",
                                label=_("Password")
                            ),
                            components.Button(
                                id="login",
                                value="Login",
                                handler="handle_login",
                                css_class="primary fluid"
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def handle_login(self):
        username = self.get_component("username").value
        password = self.get_component("password").value
        user = authenticate(username=username, password=password)

        request = self.get_request()

        if user is not None:
            if user.is_active:
                login(request, user)
                root = self.get_root()
                root.refresh_all()
                root.add_message(_("You are logged in!"), "success")
            else:
                self.add_message(_("Your account is not acitve!"), "error")
        else:
            self.add_message(_("Username and password don't match!"), "error")


class MainMenu(components.Menu):
    def init_components(self):
        self.initial_components = [
            components.MenuItem(name="Logout", handler="handle_logout"),
            components.MenuItem(name="Test", href="/test.de", default_ajax=False),
            components.MenuItem(id="about-us", name="About us", handler="handle_about_us"),
        ]

    def handle_about_us(self):
        root = self.get_root()
        root.add_component(
            components.Modal(
                id="modal-1",
                header="About us",
                initial_components=[
                    components.Text(
                        value="""Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.""")
                ]),
        )
        root.refresh()

    def handle_logout(self):
        request = self.get_request()
        logout(request)

        root = self.get_root()
        root.refresh_all()
        root.add_message(_("You are logged out!"), "success")


class NotesRoot(components.Group):
    def init_components(self):
        if self.get_request().user.is_anonymous():
            self.initial_components = [
                Login(id="login-form"),
            ]
        else:
            table = components.Table(id="table", columns=["Title", "Created", "Modified", "Show", "Edit", "Delete"])
            self.initial_components = [
                MainMenu(id="menu"),
                # layouts.Grid(
                #     id="grid",
                #     initial_components=[
                #         layouts.Column(
                #             width=14,
                #             initial_components=[
                #                 components.TextInput(label="Strasse", placeholder="Strasse"),
                #             ],
                #         ),
                #         layouts.Column(
                #             width=2,
                #             initial_components=[
                #                 components.TextInput(label="Hausnummer", placeholder="Hausnr."),
                #             ],
                #         ),
                #         layouts.Row(
                #             initial_components=[
                #                 layouts.Column(
                #                     width=4,
                #                     initial_components=[
                #                         components.TextInput(label="Hausnummer", placeholder="Hausnr."),
                #                     ],
                #                 ),
                #                 layouts.Column(
                #                     width=4,
                #                     initial_components=[
                #                         components.TextInput(label="Hausnummer", placeholder="Hausnr."),
                #                     ],
                #                 ),
                #             ],
                #         ),
                #         layouts.Column(
                #             initial_components=[
                #                 components.Button(value="Hurz!"),
                #             ],
                #         ),
                #     ],
                # ),

                components.Tabs(
                    id="tabs",
                    initial_components=[
                        components.Tab(
                            id="notes",
                            title="Notes",
                            active=True,
                            initial_components=[
                                components.Group(
                                    id="form",
                                    css_class="container form",
                                    initial_components=[
                                        components.HiddenInput(id="note-id"),
                                        components.TextInput(id="title", label="Title"),
                                        components.TextArea(id="text", label="Text"),
                                        components.Button(id="save-note", value="Add", css_class="primary", handler="handle_save_note"),
                                        table,
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ]
            self._load_notes(table)

    def _load_notes(self, table):
        table.data = []
        for note in Note.objects.all():
            table.add_data([
                note.title,
                note.created,
                note.modified,
                components.Link(id="show-note-{}".format(note.id), text="Show", handler="handle_show_note"),
                components.Link(id="edit-note-{}".format(note.id), text="Edit", handler="handle_edit_note"),
                components.Link(id="delete-note-{}".format(note.id), text="Delete", handler="handle_delete_note"),
            ])

    def handle_edit_note(self):
        note_id = self.event_id.split("-")[-1]

        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            pass
        else:
            button = self.get_component("save-note")
            button.value = "Save"

            title = self.get_component("title")
            title.value = note.title

            text = self.get_component("text")
            text.value = note.text

            note_id = self.get_component("note-id")
            note_id.value = note.id

            button.parent.refresh()

    def delete_note(self):
        note_id = self.event_id.split("-")[-1]
        try:
            Note.objects.get(pk=note_id).delete()
        except Note.DoesNotExist:
            self.add_message(_("Note doesn't exist!"), type="error")
        else:
            self.add_message(_("Note has been deleted!"), type="success")

        table = self.get_component("table")
        self._load_notes(table)
        table.refresh()

    def handle_delete_note(self):
        modal = components.ConfirmModal(
            id="modal",
            handler="delete_note",
            header=_("Delete Note!"),
            text=_("Do you really want to delete the note?"),
            event_id=self.event_id,
        )

        self.add_component(modal)
        self.refresh()

    def handle_save_note(self):

        request = self.get_request()
        if request.user.is_anonymous():
            self.add_message("Nix!")
            return

        button = self.get_component("save-note")
        note_id = self.get_component("note-id")
        title = self.get_component("title")
        text = self.get_component("text")

        if title.value == "":
            title.error = _("Title is required!")
        else:
            title.error = ""

        if text.value == "":
            text.error = _("Title is required!")
        else:
            text.error = ""

        if title.value == "" or text.value == "":
            self.add_message(_("Please correct the indicated errors!"), type="error")

        if title.value != "" and text.value != "":
            if not note_id.value:
                Note.objects.create(title=title.value, text=text.value)
                self.add_message(_("Note has been added!"), type="success")
            else:
                note = Note.objects.get(pk=note_id.value)
                note.title = title.value
                note.text = text.value
                note.save()
                self.add_message(_("Note has been modified!"), type="success")

            table = self.get_component("table")
            self._load_notes(table)
            table.refresh()

            title.clear()
            text.clear()
            note_id.clear()

            button.value = "Add"

        button.parent.refresh()

    def handle_hurz(self):
        self.add_message("Hurz!")

    def handle_show_note(self):
        note_id = self.event_id.split("-")[-1]

        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            pass
        else:
            self.add_component(
                components.Modal(
                    id="show-note-modal",
                    header=note.title,
                    initial_components=[
                        components.Text(value=note.text),
                    ]
                )
            )

        self.refresh()


class NotesView(CBAView):
    root = NotesRoot
