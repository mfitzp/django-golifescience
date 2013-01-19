import datetime
from haystack.indexes import *
from haystack import site
from methods.models import *


class MethodIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
    site_id = IntegerField(model_attr='site__id')

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Method.objects.all() #.filter(pub_date__lte=datetime.datetime.now())

site.register(Method, MethodIndex)
