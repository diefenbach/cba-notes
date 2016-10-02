from __future__ import unicode_literals, print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _

from markupfield.fields import MarkupField
from taggit.managers import TaggableManager


class Note(models.Model):
    """
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
        return html
