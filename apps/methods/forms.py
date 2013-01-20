import datetime
# Django
from django import forms
from django.contrib.admin import widgets        
from django.forms.models import inlineformset_factory, BaseModelFormSet
from django.contrib.sites.models import Site
# Methodmint                               
from methods.models import *
# External
from countries.models import Country
from haystack.forms import SearchForm
from durationfield.forms import DurationField as FDurationField
from durationfield.forms import DurationInput as WDurationInput
from taggit.forms import TagField, TagWidget
#from django_markdown.widgets import MarkdownWidget

class MethodSearchForm(SearchForm):

    def __init__(self, *args, **kwargs):
        super(MethodSearchForm, self).__init__(*args, **kwargs)
       

class MethodForm(forms.ModelForm):

    def clean_site(self):
        # Site always set to that of the parent method
        return Site.objects.get_current()

    def clean_tags(self):
        return [ x.lower() for x in self.cleaned_data['tags'] ]

    name = forms.CharField(required=True)
    description = forms.CharField(required=True)#, widget=MarkdownWidget(attrs={'cols':'25', 'rows':'5'}), help_text='Add a short description of this method.')
    notes = forms.CharField(required=False)#, widget=MarkdownWidget(attrs={'cols':'25', 'rows':'5'}), help_text='Add any additional notes.')

    materials = forms.CharField(required=False, label='Materials', widget=forms.Textarea(attrs={'cols':'25', 'rows':'1'}), help_text='List of materials needed, one per line.')

    tags = TagField(required=False, widget = TagWidget(attrs={'class': "tagsinput"}), help_text='A comma-separated list of tags.')
    
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=True, widget=forms.HiddenInput() )
 
    #author = forms.ModelChoiceField(queryset=User.objects.all(), required=True, widget=forms.HiddenInput() )

    class Meta:
        model = Method
        exclude = ('users','latest_editor','author')


class StepForm(forms.ModelForm):

    def clean_site(self):
        # Site always set to that of the parent method
        return Site.objects.get_current()

    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=True, widget=forms.HiddenInput())

    content = forms.CharField(required=True)#, widget=MarkdownWidget(attrs={'cols':'80', 'rows':'5'}))
    tip = forms.CharField(required=False)#, widget=MarkdownWidget(attrs={'cols':'60', 'rows':'5'}))

    thread = forms.IntegerField(min_value=1, max_value=5, initial=1, widget=forms.HiddenInput())
    order = forms.IntegerField(required=True, initial=0, widget=forms.HiddenInput())

    duration = FDurationField(required=False)

    class Meta:
        model = Step


    
MethodFormSet = inlineformset_factory(Method, Step, form=StepForm, extra=0, can_delete=True)


