from django.contrib.sitemaps import Sitemap
# abl.es
from blog.models import Article
from applications.models import Application
from methods.models import Method
from profiles.models import UserProfile


class MethodSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1
    limit = 1000

    def items(self):
        return Method.objects.all()

    #def location(self, obj):
    #    return obj.get_absolute_path()


class ApplicationSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1
    limit = 1000

    def items(self):
        return Application.objects.all()

class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1
    limit = 1000

    def items(self):
        return Article.objects.all()

class UserProfileSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    limit = 1000

    def items(self):
        return UserProfile.objects.all()

    def lastmod(self, obj):
        return obj.user.last_login

