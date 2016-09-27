from django.utils.translation import ugettext_lazy as _

from cba import components

import notes.components.note_edit
from notes.models import Note


class NotesTable(components.Table):
    """A Table component to display a list of Notes.
    """
    def load_notes(self, current_id=None):
        self.clear()

        if current_id is None:
            current_id = Note.objects.first().id

        for note in Note.objects.all():
            if note.id == current_id:
                css_class = "clickable selected"
            else:
                css_class = "clickable"

            self.add_component(
                components.TableRow(
                    id="show-note-{}".format(note.id),
                    handler="handle_show_note",
                    css_class=css_class,
                    initial_components=[
                        components.TableColumn(
                            initial_components=[
                                components.HTML(text=note.title)
                            ]
                        ),
                        components.TableColumn(
                            initial_components=[
                                components.HTML(text=", ".join([tag.name for tag in note.tags.all()]))
                            ]
                        ),
                        components.TableColumn(
                            initial_components=[
                                components.HTML(text=note.modified)
                            ]
                        ),
                        components.TableColumn(
                            initial_components=[
                                components.Link(id="edit-note-{}".format(note.id), text="Edit", handler="handle_edit_note"),
                            ]
                        ),
                        components.TableColumn(
                            initial_components=[
                                components.Link(id="delete-note-{}".format(note.id), text="Delete", handler="handle_delete_note"),
                            ]
                        ),
                    ]
                )
            )


class NoteView(components.Group):
    """
    The NoteView consists out of a Table component to display the list of
    notes and a HTML component to display the current selected one.
    """
    def init_components(self):
        notes_table = NotesTable(
            id="notes-table",
            label=_("Notes"),
            columns=["Title", "Tags", "Modified", "Edit", "Delete"],
        )

        note_detail = components.HTML(
            id="note-detail",
            tag="div",
            attributes={"style": "padding-top:20px"},
        )

        self.initial_components = [
            notes_table,
            note_detail,
        ]

        note_id = self.get_request().GET.get("note")
        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            note = Note.objects.first()
        if note:
            note_detail.text = note.render()

        notes_table.load_notes(note.id)

    def delete_note(self):
        note_id = self.event_id.split("-")[-1]
        try:
            Note.objects.get(pk=note_id).delete()
        except Note.DoesNotExist:
            self.add_message(_("Note doesn't exist!"), type="error")
        else:
            self.add_message(_("Note has been deleted!"), type="success")

        table = self.get_component("notes-table")
        table.load_notes()
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
            note_edit = notes.components.note_edit.NoteEdit(id="note-edit", css_class="container form")
            note_edit.set_note(note)

            main = self.get_component("main")
            main.replace_component("note-view", note_edit)
            main.refresh()

    def handle_show_note(self):
        note_id = self.event_id.split("-")[-1]
        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            pass
        else:
            note_detail = self.get_component("note-detail")
            note_detail.text = note.render()
            note_detail.refresh()

            notes_table = self.get_component("notes-table")
            notes_table.load_notes(note.id)
            notes_table.refresh()

    def set_current_note(self, note):
        note_detail = self.get_component("note-detail")
        note_detail.text = note.render()

        notes_table = self.get_component("notes-table")
        notes_table.load_notes(note.id)
