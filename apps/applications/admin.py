from django.contrib import admin
# Methodmint
from applications.models import *
from references.models import Reference
from authors.models import Author


class AuthorInline(generic.GenericTabularInline):
    model = Author

class ReferenceInline(generic.GenericTabularInline):
    model = Reference

class FeatureInline(admin.TabularInline):
    model = Feature


class OhlohInline(admin.TabularInline):
    model = Ohloh


class ApplicationAdmin(admin.ModelAdmin):
    inlines = [
        AuthorInline,
        ReferenceInline,
        OhlohInline,
    ]

admin.site.register(Application, ApplicationAdmin)
admin.site.register(Release)


