import datetime
import itertools
# Django
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
# External
# Installables
from applications.models import Application
from blog.models import Article
from methods.models import Method
from publications.models import Publication

def languages( context ):
	return { 'LANGUAGES': settings.LANGUAGES, 'LANGUAGE_CODE': context.LANGUAGE_CODE }

def modelglobals( context ):
    return {
        'all_applications': Application.objects.order_by('-name').all(),
        #'default_tagged_model': None,
    } 

def site( context ):
    return {
        'default_host': settings.DEFAULT_HOST,
#        'site': settings.SUBDOMAIN_SITES[ context.subdomain ],
#        'all_sites': settings.SUBDOMAIN_SITES,
    }

def top5s( context ):

    top5s = cache.get('top5s', None ) 
    if top5s is None:

        # Top N methods
        top5s = {
             'latest': sorted( itertools.chain(
                        Application.objects.order_by('-created_at')[:5],
                        Article.objects.order_by('-created_at')[:5],
                        Method.objects.order_by('-created_at')[:5],
                        Publication.objects.order_by('-created_at')[:5],
                    ),  key=lambda x: x.created_at, reverse=True)[:5], 

            'views': sorted( itertools.chain( 
                        Application.objects.extra(
                        select={ 'hit_count': 'SELECT hits FROM hitcount_hit_count AS t WHERE t.content_type_id=' + 
                                str(ContentType.objects.get_for_model(Application).id) + ' AND t.object_pk=applications_application.id',}
                            ,).order_by('-hit_count')[:5],
                        Article.objects.extra(
                        select={ 'hit_count': 'SELECT hits FROM hitcount_hit_count AS t WHERE t.content_type_id=' + 
                                str(ContentType.objects.get_for_model(Article).id) + ' AND t.object_pk=blog_article.id',}
                            ,).order_by('-hit_count')[:5],
                        Method.objects.extra(
                        select={ 'hit_count': 'SELECT hits FROM hitcount_hit_count AS t WHERE t.content_type_id=' + 
                                str(ContentType.objects.get_for_model(Method).id) + ' AND t.object_pk=methods_method.id',}
                            ,).order_by('-hit_count')[:5],
                        Publication.objects.extra(
                        select={ 'hit_count': 'SELECT hits FROM hitcount_hit_count AS t WHERE t.content_type_id=' + 
                                str(ContentType.objects.get_for_model(Publication).id) + ' AND t.object_pk=publications_publication.id',}
                            ,).order_by('-hit_count')[:5],
                    ),  key=lambda x: x.hit_count, reverse=True)[:5], 

            'trending': sorted( itertools.chain( 
                            Application.objects.extra(
                            select={ 'hit_count': 'SELECT COUNT(*) AS recent_hits FROM hitcount_hit_count AS t INNER JOIN hitcount_hit AS h ON h.hitcount_id = t.id WHERE h.created > (NOW() - INTERVAL 1 DAY) AND t.content_type_id=' + 
                                    str(ContentType.objects.get_for_model(Application).id) + ' AND t.object_pk=applications_application.id GROUP BY t.id',}
                                ,).order_by('-hit_count')[:5],
                            Article.objects.extra(
                            select={ 'hit_count': 'SELECT COUNT(*) AS recent_hits FROM hitcount_hit_count AS t INNER JOIN hitcount_hit AS h ON h.hitcount_id = t.id WHERE h.created > (NOW() - INTERVAL 1 DAY) AND t.content_type_id=' + 
                                    str(ContentType.objects.get_for_model(Article).id) + ' AND t.object_pk=blog_article.id GROUP BY t.id',}
                                ,).order_by('-hit_count')[:5],
                            Method.objects.extra(
                            select={ 'hit_count': 'SELECT COUNT(*) AS recent_hits FROM hitcount_hit_count AS t INNER JOIN hitcount_hit AS h ON h.hitcount_id = t.id WHERE h.created > (NOW() - INTERVAL 1 DAY) AND t.content_type_id=' + 
                                    str(ContentType.objects.get_for_model(Method).id) + ' AND t.object_pk=methods_method.id GROUP BY t.id',}
                                ,).order_by('-hit_count')[:5],
                            Publication.objects.extra(
                            select={ 'hit_count': 'SELECT COUNT(*) AS recent_hits FROM hitcount_hit_count AS t INNER JOIN hitcount_hit AS h ON h.hitcount_id = t.id WHERE h.created > (NOW() - INTERVAL 1 DAY) AND t.content_type_id=' + 
                                    str(ContentType.objects.get_for_model(Publication).id) + ' AND t.object_pk=publications_publication.id GROUP BY t.id',}
                                ,).order_by('-hit_count')[:5],
                    ),  key=lambda x: x.hit_count, reverse=True)[:5], 
        }

        cache.set('top5s', top5s ) 
    return {
        'top5s': top5s
    }

