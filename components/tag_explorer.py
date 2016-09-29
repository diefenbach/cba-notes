from django.utils.translation import ugettext_lazy as _
from taggit.models import Tag
from cba import components


class TagExplorer(components.Group):
    def init_components(self):
        self.initial_components = []
        self.load_tags()

    def load_tags(self):
        for tag in Tag.objects.all():
            self.initial_components.append(
                components.Link(id="tag-{}".format(tag.id), text=tag.name, handler="handle_select_tag")
            )

        self.initial_components.append(
            components.HTML(
                tag="div",
                attributes={"style": "padding-top: 20px; font-weight: bold"},
                initial_components=[
                    components.Link(
                        attributes={"style": "color: red"},
                        id="reset-tags",
                        text=_("Reset Tags"),
                        handler="handle_reset_tags")
                ])
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
