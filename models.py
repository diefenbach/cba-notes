from __future__ import unicode_literals, print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager


class Note(models.Model):
    title = models.CharField(_("Title"), max_length=50)
    text = models.TextField(_(u"Text"))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    tags = TaggableManager()
