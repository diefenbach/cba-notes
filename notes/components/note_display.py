from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from cba import components
from cba import utils

# Circular import
import notes.components.note_edit
from notes.models import Note


class NotesTableDataProvider(components.TableDataProvider):
    def total_rows(self):
        return Note.objects.count()

    def get_rows(self, start, end):
        selected_tag_id = utils.get_from_session("selected-tag-id")
        search = utils.get_from_session("search")

        if selected_tag_id:
            query = Note.objects.filter(tags__id=selected_tag_id)
        else:
            query = Note.objects.all()

        if search:
            query = query.filter(
                Q(title__contains=search) |
                Q(text__contains=search) |
                Q(tags__name__contains=search)
            )

        current_note_id = utils.get_from_session("current-note-id")
        notes = []
        for note in query[start:end]:
            if note.id == current_note_id:
                selected = True
            else:
                selected = False

            notes.append({
                "css_class": "clickable",
                "component_value": note.id,
                "selected": selected,
                "data": [
                    note.title,
                    ", ".join([tag.name for tag in note.tags.all()]),
                    note.modified,
                    components.HTML(
                        tag="i",
                        id="delete-note-{}".format(note.id),
                        handler={"click": "server:handle_delete_note"},
                        css_class="red large remove icon"
                    ),
                ]
            })

        return notes

    def get_headers(self):
        return [_("Title"), _("Tags"), _("Modified"), _("Delete")]


class NoteDisplay(components.Group):
    """Display the list of notes and the current note.
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

        self.notes_table = components.Table(
            id="notes-table",
            label=_("Notes"),
            data_provider=NotesTableDataProvider(),
        )

        self.note_detail = components.HTML(
            id="note-detail",
            tag="div",
            css_class="clickable mt",
            handler={"click": "server:handle_edit_note"},
        )

        self.images = components.Group(id="images")

        self.initial_components = [
            self.search,
            self.notes_table,
            self.note_detail,
            self.images,
        ]

        self.load_current_note()

    def delete_note(self):
        """Deletes a note.

        The note id is store within the event_id attribute.
        """
        if self.component_value:
            note_id = self.component_value.split("-")[-1]
            try:
                Note.objects.get(pk=note_id).delete()
            except Note.DoesNotExist:
                self.add_message(_("Note doesn't exist!"), type="error")
            else:
                self.add_message(_("Note has been deleted!"), type="success")

            self.load_current_note()

        self.remove_component(self.component_id)
        self.refresh()

        tag_explorer = self.get_component("tag-explorer")
        tag_explorer.refresh_all()

    def handle_delete_note(self):
        """Handles click on the delete link of a note.
        """
        note_id = self.component_value.split("-")[-1]
        note = Note.objects.get(pk=note_id)

        modal = components.ConfirmModal(
            id="modal",
            handler="delete_note",
            header=_("Delete Note!"),
            text=_("Do you really want to delete the note with the title \"{}\"?".format(note.title)),
            component_value=self.component_value,
        )

        self.add_component(modal)
        self.refresh()

    def handle_edit_note(self):
        """Handles click on the edit link of a note.
        """
        note_id = utils.get_from_session("current-note-id")

        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            pass
        else:
            note_edit = notes.components.note_edit.NoteEdit(id="note-edit", css_class="container form")

            note_edit.get_component("note-id").value = note.id
            note_edit.get_component("title").value = note.title
            note_edit.get_component("text").value = note.text.raw
            note_edit.get_component("tags").value = [tag.name for tag in note.tags.all()]
            note_edit.get_component("files").existing_files = note.file_set.all()

            main = self.get_component("main")
            main.replace_component("note-view", note_edit)
            main.refresh()

    def handle_search(self):
        utils.set_to_session("search", self.search.value)
        self.load_current_note()

        self.note_detail.refresh()
        self.notes_table.refresh()

    def handle_show_note(self):
        """Handles click to a table row of a note.
        """
        for row in self.get_component("notes-table").components:
            row.selected = False

        self.get_component(self.component_id).selected = True

        note_id = self.component_value
        try:
            note = Note.objects.get(pk=note_id)
        except Note.DoesNotExist:
            pass
        else:
            utils.set_to_session("current-note-id", note_id)
            note_detail = self.get_component("note-detail")
            note_detail.content = note.render()
            note_detail.refresh()

    def load_current_note(self):
        """Loads the current note.

        Loads the current note into the table and detail view.
        """
        selected_tag_id = utils.get_from_session("selected-tag-id")
        current_note_id = utils.get_from_session("current-note-id")
        search = utils.get_from_session("search")

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
                current_note_id = current_note.id
                current_note_text = current_note.render()
            else:
                current_note_id = None
                current_note_text = ""

        self.note_detail.content = current_note_text

        if current_note:
            utils.set_to_session("current-note-id", current_note.id)

        self.notes_table.load_data()
