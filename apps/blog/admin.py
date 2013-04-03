from django.contrib import admin
from django_markdown.admin import MarkdownModelAdmin
# abl.es
from models import *

admin.site.register(Article, MarkdownModelAdmin)

#admin.site.register(Article)

