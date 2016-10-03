from django.contrib import admin

from . models import Note
from . models import File


admin.site.register(File)
admin.site.register(Note)
