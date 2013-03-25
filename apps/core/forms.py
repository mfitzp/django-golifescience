from django.conf import settings
from django.db import models
from django import forms
from django.contrib.auth.models import User
# External
from registration.forms import RegistrationForm

class LoginForm(forms.Form):
    username = forms.CharField( max_length=100 )
    password = forms.CharField( widget=forms.PasswordInput(render_value=False),max_length=100 )

class RegistrationFormNoBlacklistEmail(RegistrationForm):
    
    def clean_email(self):
        """
        Check the supplied email address against a list of known free
        webmail domains.
        
        """
        email_domain = self.cleaned_data['email'].split('@')[1]
        if email_domain in settings.BLACKLIST_EMAIL_DOMAINS:
            raise forms.ValidationError(_("Registration using that email address is prohibited. Please supply a different email address."))
        return self.cleaned_data['email']