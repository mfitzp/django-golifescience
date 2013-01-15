from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
# abl.es
from models import *

class LatestArticlesFeed(Feed):
    title = "Latest articles"
    link = "/blog/rss/"
    description = "Latest articles added to the site"

    def items(self):
        return Article.on_site.order_by('-created_at')[:30]
        
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content
        
    def item_pubdate(self, item):
        return item.created_at
        
