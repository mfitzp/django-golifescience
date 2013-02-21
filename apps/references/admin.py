from django.contrib import admin
# Methodmint
from references.models import *

class ReferenceAdmin(admin.ModelAdmin):
    fields = ('uri','namespace', 'title', 'description', 'author', 'publisher', 'published',)
    readonly_fields =('namespace', 'title', 'description', 'author', 'publisher', 'published',)


admin.site.register(Reference, ReferenceAdmin)

