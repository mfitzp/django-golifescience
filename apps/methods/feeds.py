import settings, os
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
import markdown
# Methodmint
from methods.models import *

class LatestMethodsFeed(Feed):
    title = "Latest methods"
    link = "/methods/rss/"
    description = "Latest methods added to the site"

    def items(self):
        return Method.objects.order_by('-created_at')[:30] 
        
    def item_title(self, item):
        return item.name

    def item_description(self, item):
       return markdown.markdown(item.description)

    def item_pubdate(self, item):
        return item.created_at

            
    def item_enclosure_url(self, item):
        if item.image:
            return '%s%s' % (settings.MEDIA_URL, item.image)
                    
    def item_enclosure_length(self, item):
        if item.image:
            statinfo = os.stat(item.image.path)
            return statinfo.st_size
            
    item_enclosure_mime_type = "image/jpeg"
        
