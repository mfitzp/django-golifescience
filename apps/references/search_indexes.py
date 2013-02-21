import datetime
from haystack import indexes
from references.models import *

'''
class ReferenceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True) #name, description 

    def get_model(self):
        return Reference

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

'''
