import datetime
# Django
from django import forms
from django.contrib.admin import widgets        
from django.forms.models import inlineformset_factory, BaseModelFormSet
from django.contrib.sites.models import Site
# Methodmint                               
from models import *
#from reference.models import Reference
# External
'''
from taggit.forms import TagField, TagWidget
from django_markdown.widgets import MarkdownWidget

class ArticleForm(forms.ModelForm):

    def clean_site(self):
        return Site.objects.get_current()

    def clean_tags(self):
        return [ x.lower() for x in self.cleaned_data['tags'] ]

    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'size':'80'}))
    content = forms.CharField(required=True, widget=MarkdownWidget(attrs={'cols':'80', 'rows':'10'}), help_text='Write your story in here. Markdown syntax is supported.')

    tags = TagField(required=False, widget = TagWidget(attrs={'class': "tagsinput"}), help_text='A comma-separated list of tags.')
    
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=True, widget=forms.HiddenInput(), initial=Site.objects.get_current() )

    class Meta:
        model = Article
        exclude = ('latest_editor','author')
'''
