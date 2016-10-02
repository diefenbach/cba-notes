from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from cba import components
from cba import layouts

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
                    handler={"click": "server:handle_show_note"},
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
                                components.HTML(
                                    tag="i",
                                    id="delete-note-{}".format(note.id),
                                    handler={"click": "server:handle_delete_note"},
                                    css_class="red large remove icon"
                                ),
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
        self.search = components.TextInput(
            id="search",
            css_class="padding-bottom",
            icon="search",
            icon_position="right",
            placeholder=_("Search"),
            handler={"keyup": "server:handle_search"},
        )

        self.notes_table = NotesTable(
            id="notes-table",
            label=_("Notes"),
            columns=[_("Title"), _("Tags"), _("Modified"), _("Delete")],
        )

        self.note_detail = components.HTML(
            id="note-detail",
            tag="div",
            css_class="clickable",
            attributes={"style": "padding-top:20px"},
            handler={"click": "server:handle_edit_note"},
        )

        # self.initial_components = [
        #     layouts.Split(
        #         initial_components=[
        #             self.notes_table,
        #             self.note_detail,
        #         ]
        #     )
        # ]

        self.initial_components = [
            self.search,
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

        self.load_current_note()
        self.refresh()

    def handle_delete_note(self):
        """Handles click on the delete link of a note.
        """
        note_id = self.event_id.split("-")[-1]
        note = Note.objects.get(pk=note_id)

        modal = components.ConfirmModal(
            id="modal",
            handler="delete_note",
            header=_("Delete Note!"),
            text=_("Do you really want to delete the note with the title \"{}\"?".format(note.title)),
            event_id=self.event_id,
        )

        self.add_component(modal)
        self.refresh()

    def handle_edit_note(self):
        """Handles click on the edit link of a note.
        """
        note_id = self.get_from_session("current-note-id")

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

    def handle_search(self):
        self.set_to_session("search", self.search.value)
        self.load_current_note()

        self.note_detail.refresh()
        self.notes_table.refresh()

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
        search = self.get_from_session("search")

        if selected_tag_id:
            notes = Note.objects.filter(tags__id=selected_tag_id)
        else:
            notes = Note.objects.all()

        if search:
            notes = notes.filter(
                Q(title__contains=search) |
                Q(text__contains=search) |
                Q(tags__name__contains=search)
            )

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
