import datetime
# Django
from django import forms
from django.contrib.admin import widgets        
from django.forms.models import inlineformset_factory, BaseModelFormSet
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
# Methodmint                               
from applications.models import *
# External
from countries.models import Country
from haystack.forms import SearchForm
from durationfield.forms import DurationField as FDurationField
from durationfield.forms import DurationInput as WDurationInput
from taggit.forms import TagField, TagWidget
#from django_markdown.widgets import MarkdownWidget

class ApplicationForm(forms.ModelForm):

    def clean_tags(self):
        return [ slugify(x) for x in self.cleaned_data['tags'] ]

    name = forms.CharField(required=True)
    tagline = forms.CharField(required=True)
    description = forms.CharField(required=True, help_text='Add a short description of this application.', widget=forms.Textarea) #, widget=MarkdownWidget(attrs={'cols':'25', 'rows':'5'})


    url = forms.CharField(required=False, label='URL', help_text='Web site URL for this software, e.g. the project homepage')
    source_url = forms.CharField(required=False, label='Source code URL', help_text='Where can we find the source code (if available), e.g. the a github address')
    
#    image = forms.ImageField(required=False)    

#    license = LicenseField(required=False, help_text='Choose the correct open-source license if applicable, else select Proprietary')

    tags = TagField(required=False, widget = TagWidget(attrs={'class': "tagsinput"}), help_text='A comma-separated list of tags.')
    
    #author = forms.ModelChoiceField(queryset=User.objects.all(), required=True, widget=forms.HiddenInput() )

    class Meta:
        model = Application
        exclude = ('created_at','created_by','edited_at','edited_by','slug','icon')


