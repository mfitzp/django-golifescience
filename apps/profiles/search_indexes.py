import datetime
from haystack.indexes import *
from haystack import site
from taggit.models import Tag
# Django

# Methodmint
from profiles.models import UserProfile

# External models 
class ProfileIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
    
    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return UserProfile.objects.all() #.filter(pub_date__lte=datetime.datetime.now())
        
site.register(UserProfile, ProfileIndex)
