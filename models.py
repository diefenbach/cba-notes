from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Note(models.Model):
    title = models.CharField(_("Title"), max_length=50)
    text = models.TextField(_(u"Text"))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
