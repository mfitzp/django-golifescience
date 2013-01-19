from django.contrib import admin
# Externals

# Methodmint
from methods.models import *
from reference.models import Reference

class StepInline(admin.TabularInline):
    model = Step

class MethodAdmin(admin.ModelAdmin):
    inlines = [
        StepInline,
    ]

admin.site.register(Method, MethodAdmin)
admin.site.register(Step)

#admin.site.register(UserMethod)

