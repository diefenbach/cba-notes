from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from taggit.models import Tag

from cba import components


class TagExplorer(components.Menu):
    def __init__(self, *args, **kwargs):
        super(TagExplorer, self).__init__(*args, **kwargs)
        self.direction = "vertical"

    def init_components(self):
        self.initial_components = []
        self.load_tags()

    def load_tags(self):
        self.initial_components.append(
            components.HTML(
                tag="div",
                initial_components=[
                    components.MenuItem(
                        attributes={"style": "color:red"},
                        id="reset-tags",
                        name=_("Reset"),
                        handler={"click": "server:handle_reset_tags"})
                ])
        )

        for tag in Tag.objects.annotate(note_count=Count("note")).filter(note_count__gt=0).order_by("-note_count"):
            self.initial_components.append(
                components.MenuItem(
                    id="tag-{}".format(tag.id),
                    name="{}".format(tag.name),
                    label=tag.note_count,
                    handler={"click": "server:handle_select_tag"})
            )


    def handle_reset_tags(self):
        self.set_to_session("selected-tag-id", None)
        notes_view = self.get_component("note-view")
        notes_view.load_current_note()
        notes_view.refresh()

    def handle_select_tag(self):
        tag_id = self.event_id.split("-")[1]
        self.set_to_session("selected-tag-id", tag_id)
        notes_view = self.get_component("note-view")
        notes_view.load_current_note()
        notes_view.refresh()
