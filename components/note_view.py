from django.utils.translation import ugettext_lazy as _

from cba import components

# Circular import
import notes.components.note_edit
from notes.models import Note


class NotesTable(components.Table):
    """A Table component to display a list of notes.
    """
    def load_notes(self, notes, current_note_id=None):
        """Load notes as table rows and columns into the table.
        """
        self.clear()
        for note in notes:
            if str(note.id) == str(current_note_id):
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
    """The NoteView consists out of a Table component to display the list of
    notes and a HTML component to display the current selected note.
    """
    def init_components(self):
        self.notes_table = NotesTable(
            id="notes-table",
            label=_("Notes"),
            columns=["Title", "Tags", "Modified", "Edit", "Delete"],
        )

        self.note_detail = components.HTML(
            id="note-detail",
            tag="div",
            attributes={"style": "padding-top:20px"},
        )

        self.initial_components = [
            self.notes_table,
            self.note_detail,
        ]

        self.load_current_note()

    def delete_note(self):
        """Deletes a note.

        The note id is store within the event_id attribute.
        """
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
        """Handles click on the delete link of a note.
        """
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
        """Handles click on the edit link of a note.
        """
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
        """Handles click to a table row of a note.
        """
        note_id = self.event_id.split("-")[-1]
        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            pass
        else:
            self.set_to_session("current-note-id", note_id)
            note_detail = self.get_component("note-detail")
            note_detail.text = note.render()
            note_detail.refresh()

    def load_current_note(self):
        """Loads the current note.

        Loads the current note into the table and detail view.
        """
        selected_tag_id = self.get_from_session("selected-tag-id")
        current_note_id = self.get_from_session("current-note-id")

        if selected_tag_id:
            notes = Note.objects.filter(tags__id=selected_tag_id)
        else:
            notes = Note.objects.all()

        if notes.filter(pk=current_note_id).exists():
            current_note = Note.objects.get(pk=current_note_id)
            current_note_id = current_note.id
            current_note_text = current_note.render()
        else:
            current_note = notes.first()
            if current_note:
                self.set_to_session("current-note-id", current_note.id)
                current_note_id = current_note.id
                current_note_text = current_note.render()
            else:
                current_note_id = None
                current_note_text = ""

        self.notes_table.load_notes(notes, current_note_id)
        self.note_detail.text = current_note_text
