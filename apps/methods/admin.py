from django.contrib import admin
from django.contrib.contenttypes import generic
# Externals

# Methodmint
from methods.models import *
from references.models import Reference, AutoReference
from authors.models import Author

class StepInline(admin.TabularInline):
    model = Step

class AuthorInline(generic.GenericTabularInline):
    model = Author

class ReferenceInline(generic.GenericTabularInline):
    model = Reference

class AutoReferenceInline(generic.GenericTabularInline):
    model = AutoReference
    max_num = 1
    extra = 0

class MethodAdmin(admin.ModelAdmin):
    inlines = [
        StepInline, 
        AuthorInline,
        ReferenceInline,
    ]

admin.site.register(Method, MethodAdmin)

