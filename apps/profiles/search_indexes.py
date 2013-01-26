import datetime
from haystack import indexes
# Django

# Methodmint
from profiles.models import UserProfile

# External models 
class ProfileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True) #name, description 

    def get_model(self):
        return UserProfile

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
