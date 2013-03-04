# Python
from datetime import date as date, datetime, timedelta
# Django
from django.db import models
from django.db.models.base import ModelBase
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted, comment_will_be_posted
from django.contrib.auth.models import AnonymousUser
# Methodmint
# Externals
from mptt.models import MPTTModel, TreeForeignKey


class MPTTComment(MPTTModel, Comment):
    """ Threaded comments - Add support for the parent comment store and MPTT traversal"""
    # a link to comment that is being replied, if one exists
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    title = models.CharField('Title', max_length = 50, blank = False)

    class MPTTMeta:
        # comments on one level will be ordered by date of creation
        order_insertion_by=['submit_date']
    
    class Meta:
        ordering=['tree_id','lft']


# Akismet spam filtering

from django.contrib.comments.signals import comment_was_posted
from django.utils.encoding import smart_str
from django.core.mail import mail_managers
import akismet
from django.conf import settings
from django.contrib.sites.models import Site

def moderate_comment(sender, comment, request, **kwargs):
    ak = akismet.Akismet(
        key = settings.AKISMET_API_KEY,
            blog_url = 'http://%s/' % Site.objects.get_current().domain
)
    data = {
        'user_ip': request.META.get('REMOTE_ADDR', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERRER', ''),
        'comment_type': 'comment',
        'comment_author': smart_str(comment.user_name),
    }
    if ak.comment_check(smart_str(comment.comment), data=data, build_data=True):
        comment.is_public = False
        comment.save()

    if comment.is_public:   
        email_body = "%s"
        mail_managers ("New comment posted", email_body % (comment.get_as_text()))


from actstream import action

# Saving of method object
def comment_posted(sender, comment, request, **kwargs):
    if not (comment.user is None or isinstance(comment.user, AnonymousUser)):
        action.send(comment.user, verb='comment', action_object=comment, target=comment.content_object)



#comment_will_be_posted.connect(moderate_comment)
comment_was_posted.connect(comment_posted)





