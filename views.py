from __future__ import print_function, unicode_literals

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _


from cba import components
from cba.views import CBAView

from . models import Note


class Login(components.Group):
    def init_components(self):
        self.initial_components = [
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
                css_class="primary"
            ),
        ]

    def handle_login(self):
        self.get_root().refresh()
        return

        username = self.get_component("username").value
        password = self.get_component("password").value
        user = authenticate(username=username, password=password)

        root = self.get_root()
        request = root.request
        root.request = None

        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                # Return a 'disabled account' error message
                pass
        else:
            # Return an 'invalid login' error message.
            pass

        self.get_root().refresh()


class NotesRoot(components.Group):

    def init_components(self):
        table = components.Table(id="table", columns=["Title", "Text", "Created", "Modified", "Edit", "Delete"])

        if 0:
            self.initial_components = [
                Login(id="login-form"),
            ]
        else:
            self.initial_components = [
                components.Tabs(
                    id="tabs",
                    initial_components=[
                        components.Tab(
                            id="notes",
                            title="Notes",
                            active=True,
                            initial_components=[
                                components.Group(id="form", initial_components=[
                                    components.TextInput(id="title", label="Title"),
                                    components.TextArea(id="text", label="text"),
                                    components.HiddenInput(id="note-id"),
                                    components.Button(id="save-note", value="Add", css_class="primary", default_ajax=True, handler="handle_save_note"),
                                    table,
                                ])
                            ]
                        )

                    ]
                )
            ]
            self._load_notes(table)

    def _load_notes(self, table):
        table.data = []
        for note in Note.objects.all():
            table.add_data([
                note.title,
                note.text,
                note.created,
                note.modified,
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
            self.add_message("Note doesn't exist!", type="error")
        else:
            self.add_message("Note has been deleted!", type="success")

        table = self.get_component("table")
        self._load_notes(table)
        table.refresh()

    def handle_delete_note(self):
        modal = components.Modal(
            id="modal",
            handler="delete_note",
            header=_("Delete Note!"),
            text=_("Do you really want to delete the note?"),
            event_id=self.event_id,
        )

        self.add_component(modal)
        self.refresh()

    def handle_save_note(self):
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

            title.value = ""
            title.error = ""
            text.value = ""
            text.error = ""
            note_id.value = ""
            button.value = "Add"

        button.parent.refresh()


class NotesView(CBAView):
    root = NotesRoot
