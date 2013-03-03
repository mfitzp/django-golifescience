import datetime
# Django
from django import forms
from django.contrib.admin import widgets        
from django.forms.models import inlineformset_factory, BaseModelFormSet
from django.contrib.sites.models import Site
# Methodmint                               
from publications.models import *

class PublicationForm(forms.ModelForm):
    uri = forms.CharField(required=True)

    class Meta:
        model = Publication

