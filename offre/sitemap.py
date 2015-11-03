from django.contrib.sitemaps import Sitemap
from offre.models import Offer
from datetime import datetime
from django.core.urlresolvers import reverse


class OfferSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return Offer.objects.all().filter(activated=True)

    def lastmod(self, obj):
        return obj.created

    def location(self, obj):
        return obj.get_absolute_url()

class SiteSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def __init__(self, names):
        self.names = names

    def items(self):
        return self.names

    def lastmod(self, obj):
        return datetime.now()

    def location(self, obj):
        return reverse(obj)
