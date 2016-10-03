from __future__ import unicode_literals, print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _

from markupfield.fields import MarkupField
from taggit.managers import TaggableManager


class File(models.Model):
    """Files belonging to a note.
    """
    note = models.ForeignKey("Note", blank=True, null=True)
    file = models.FileField()


class Note(models.Model):
    """A note.
    """
    def __unicode__(self):
        return "{} - {}".format(self.id, self.title)

    title = models.CharField(_("Title"), max_length=50)
    text = MarkupField(_("Text"), markup_type='markdown')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def render(self):
        html = "<h1>{}</h1>".format(self.title)
        html += "<p>{}</p>".format(", ".join(self.tags.names()))
        html += "<p>{}</p>".format(self.text)

        if self.file_set.all():
            html += "<h2>Images</h2>"
            for file in self.file_set.all():
                html += "<img src='{}' width='100px' /> ".format(file.file.url)

        return html
