from django.conf.urls.defaults import *
# Methodmint
from discuss.feeds import *
from discuss.models import Thread

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^$', 'discuss.views.overview', name='discuss' ),

    url(r'^(?P<forum_id>\d+)/$', 'discuss.views.forum', name='discuss_forum' ),
    url(r'^(?P<forum_id>\d+)/newthread/$', 'discuss.views.newthread', name='discuss_newthread' ),

    url(r'^thread/(?P<thread_id>\d+)/$', 'discuss.views.thread', name='discuss_thread' ),
    url(r'^thread/(?P<thread_id>\d+)/reply/$', 'discuss.views.reply', name='discuss_reply' ),

    url(r'^post/(?P<post_id>\d+)/$', 'discuss.views.post', name='discuss_post' ),
    url(r'^thread/(?P<thread_id>\d+)/#post-(?P<post_id>\d+)$', 'discuss.views.thread', name='discuss_post_permalink' ),

    url(r'^rss/posts/$', LatestEntriesFeed(), name='discuss_rss_posts'),
    url(r'^rss/threads/$', LatestThreadsFeed(), name='discuss_rss_threads'),
    url(r'^(?P<forum_id>\d+)/rss/$', ForumLatestThreadsFeed(), name='discuss_rss_forum_threads'),
    url(r'^thread/(?P<thread_id>\d+)/rss/$', LatestThreadEntriesFeed(), name='discuss_rss_thread_posts'),

    url(r'^o/(?P<content_type_id>\d+)/(?P<object_pk>\d+)/$', 'discuss.views.object_forum', name='discuss_object' ),
    url(r'^o/(?P<content_type_id>\d+)/(?P<object_pk>\d+)/newthread/$', 'discuss.views.forum', name='discuss_object_newthread' ),


    url(r'^thread/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', 'voting.views.vote_on_object', {
        'model': Thread,
        'template_object_name': 'thread',
        'allow_xmlhttprequest': 'true',
        }, 
        name='thread-voting'),

    url(r'^post/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', 'voting.views.vote_on_object', {
        'model': Post,
        'template_object_name': 'post',
        'allow_xmlhttprequest': 'true',
        }, 
        name='post-voting'),
 
)

