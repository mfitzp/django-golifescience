import datetime
from haystack.indexes import *
from haystack import site
from taggit.models import Tag

# External models 
class TagIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
    
    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Tag.objects.all() #.filter(pub_date__lte=datetime.datetime.now())
        
site.register(Tag, TagIndex)
