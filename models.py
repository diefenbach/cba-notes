from __future__ import unicode_literals, print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager


class Note(models.Model):
    """
    """
    def __unicode__(self):
        return "{} - {}".format(self.id, self.title)

    title = models.CharField(_("Title"), max_length=50)
    text = models.TextField(_(u"Text"))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def get_tags_as_string(self):
        return ", ".join([tag.name for tag in self.tags.all()])
