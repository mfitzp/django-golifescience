import settings, os
import itertools
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.db.models import Sum
import markdown
# Methodmint
from methods.models import *
#from questions.models import *
from blog.models import *
from applications.models import *
from publications.models import *

# This is fecking ugly because of the variations in model structure/naming (name vs. titlel; content vs. description)
# would be lovely to get a consistent interface (at least) to all of this

class LatestAllFeed(Feed):
    title = "Latest content"
    link = "/rss/latest/"
    description = "Latest content on the site"

    def items(self):    ## thanks to http://demongin.org/blog/780/ for sorted combined entries
        results = itertools.chain(
            Method.objects.order_by('-created_at')[:20],
            Article.objects.order_by('-created_at')[:20],
            Application.objects.order_by('-created_at')[:20],
            Publication.objects.order_by('-created_at')[:20],
        ) 

        return sorted(results, key=lambda x: x.created_at, reverse=True)

    def build_from(self, item, l):
        result = []
        for attr in l:
            result.append(getattr(item, attr, ''))
        return " ".join(result)

    def item_title(self, item):
        return self.build_from(item, ['name', 'title', 'tagline'])

    def item_description(self, item):
        return self.build_from(item, ['description', 'content'])

    def item_pubdate(self, item):
        return item.created_at
            
    def item_enclosure_url(self, item):
        try:
            if item.image:
                return 'http://%s%s' % (settings.DEFAULT_HOST, item.image.url)
        except:
            return None

    def item_enclosure_length(self, item):
        if item.image:
            statinfo = os.stat(item.image.path)
            return statinfo.st_size
            
    item_enclosure_mime_type = "image/jpeg"

class LatestAllFeedTwitter(LatestAllFeed):
    title = "Latest content formatted for twitter syndication"
    link = "/rss/latest/twitter/"
    description = "Latest content on the site formatted for twitter"

    def item_title(self, item):
        # Twitter is restricted to 140 characters so do some fancies
        title = self.build_from(item, ['name', 'title', 'tagline'])

        hashtags = list()

        if hasattr(item, 'tags'):
            # Now get tags off the item; only those with root metadata (important tags) and add to beginning of list
            # Optionally supports >1 root metatag (could happen)
            tags = item.tags.exclude(meta__tag_id=None).filter(meta__parent=None).order_by('?')[:3]
            if tags:
                for tag in tags:
                    hashtags.append( tag.slug.replace('-', '') ) # Use slug to remove most funky stuff, then - since hashtags tend to be bunched

            hashtags = filter(None, hashtags)
            hashtags = ['#' + x for x in hashtags[:3] ] # Limit to 3 tags total
            hashtagstr = ' ' + ' '.join( hashtags )

            # Trim the title down to meet the 140 char limit and return the joined content
            title = title[:140- ( len(hashtagstr) + 13 )]  # Magic 13 = bitly url length
            return title + hashtagstr 
        else:
            return title


    def item_description(self, item):
        return '' # Blank out, we have the character limit
            
    def item_enclosure_url(self, item):
        return '' # Blank out it's twitter



from disqus.wxr_feed import ContribCommentsWxrFeed
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
class CommentsWxrFeed(ContribCommentsWxrFeed,LatestAllFeed):
    link = "/rss/comments/WxR/"

    def items(self):    ## Items with comments
        
        results = list( itertools.chain(
            Method.objects.all(),
            Article.objects.all(),
#            Application.objects.order_by('-created_at')[:20],
#            Publication.objects.order_by('-created_at')[:20],
        ) )

        results_with_comments = []
        for r in results:
            ctype = ContentType.objects.get_for_model(r)
            
            c = Comment.objects.filter(
                content_type = ctype,
                object_pk    = r.id,
            ).count()
            if c > 0:
                results_with_comments.append( r ) 

        return results_with_comments

