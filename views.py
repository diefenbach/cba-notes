from __future__ import print_function, unicode_literals

from django.utils.translation import ugettext_lazy as _

from taggit.models import Tag
from cba import components
from cba.views import CBAView

from notes.models import Note
from notes.components.login import Login
from notes.components.main_menu import MainMenu


class NotesRoot(components.Group):
    def init_components(self):
        if self.get_request().user.is_anonymous():
            self.initial_components = [
                Login(id="login-form"),
            ]
        else:
            table = components.Table(id="table", columns=["Title", "Tags", "Modified", "Show", "Edit", "Delete"])
            tags_select = components.Select(id="tags", label="Tags")

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
                                        tags_select,
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
            self._load_tags(tags_select)

    def _load_tags(self, select):
        select.options = []
        for tag in Tag.objects.all().order_by("name"):
            select.options.append({
                "name": tag.name,
                "value": tag.name,
            })

    def _load_notes(self, table):
        table.data = []
        for note in Note.objects.all():
            table.add_data([
                note.title,
                ", ".join([tag.name for tag in note.tags.all()]),
                note.modified,
                components.Link(id="show-note-{}".format(note.id), text="Show", handler="handle_show_note"),
                components.Link(id="edit-note-{}".format(note.id), text="Edit", handler="handle_edit_note"),
                components.Link(id="delete-note-{}".format(note.id), text="Delete", handler="handle_delete_note"),
            ])

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

            tags = self.get_component("tags")
            tags.value = [tag.name for tag in note.tags.all()]

            button.parent.refresh()

    def handle_save_note(self):
        request = self.get_request()
        print(request.POST)
        if request.user.is_anonymous():
            self.add_message("Nix!")
            return

        button = self.get_component("save-note")
        note_id = self.get_component("note-id")
        title = self.get_component("title")
        text = self.get_component("text")
        tags = self.get_component("tags")

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
            title.refresh()
            text.refresh()

        if title.value != "" and text.value != "":
            if not note_id.value:
                note = Note.objects.create(title=title.value, text=text.value)
                self.add_message(_("Note has been added!"), type="success")
            else:
                note = Note.objects.get(pk=note_id.value)
                note.title = title.value
                note.text = text.value

                self.add_message(_("Note has been modified!"), type="success")

            note.tags.all().delete()
            for value in tags.value:
                note.tags.add(value)
            note.save()

            table = self.get_component("table")
            self._load_notes(table)
            self._load_tags(tags)

            table.refresh()

            title.clear()
            text.clear()
            note_id.clear()
            tags.clear()

            button.parent.refresh()

            button.value = _("Add")

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
                        components.HTML(tag="p", text="<br/><br/><b>Tags:</b> {}".format(note.get_tags_as_string())),
                    ]
                )
            )

        self.refresh()


class NotesView(CBAView):
    root = NotesRoot
