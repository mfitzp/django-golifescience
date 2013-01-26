import datetime
from haystack import indexes
from methods.models import *


class MethodIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True) #name, description 

    def get_model(self):
        return Method

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
