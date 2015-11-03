# -*- coding: utf-8 -*-
from django.db import models
from django.db import models, IntegrityError

from car_shop.model_choices import *
from car_shop.random_unique import RandomPrimaryIdModel
import profile

import datetime
import math
from offre.managers import OfferManager
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sitemaps import ping_google

from uuid import uuid4
import subprocess
from django.conf import settings
from PyPDF2 import PdfFileReader, PdfFileWriter

from datetime import date, timedelta
from django.db.models.signals import post_save, post_delete

# slugify title field
import re
from django.template.defaultfilters import slugify

# for the bigest item in the dictionary
import operator
import logging


from django.db.models.signals import post_save, post_delete
from caching.caching import cache_update, cache_evict


class Offer(RandomPrimaryIdModel):
    """ Modele pour les offres de travail """
    user        = models.ForeignKey(User)

    title       = models.CharField(max_length=250)
    slug        = models.CharField(verbose_name = u'Titre automatique', max_length=250, blank=True, default='', unique=True)

    offerType   = models.CharField( _('type de l\'offre '), max_length = 200, choices=OFFER_CHOICES, default='1')
    category    = models.CharField( _('categorie'), max_length = 200, choices=CATEGORY_CHOICES, default='1')
    town        = models.CharField(_('ville'),max_length = 200, blank=True, default="")
    postal_code = models.CharField(_('Code postal'),max_length = 200, blank=True, default="")
    city        = models.CharField(max_length = 200, choices=DEPARTEMENT_CHOICES)

    region      = models.CharField(max_length = 200, choices=REGION_CHOICES)
    salary      = models.CharField( _('salaire'), max_length = 200, blank=True, choices=SALARY_CHOICES)
    study_level = models.CharField(verbose_name = u'Niveau d\'etudes', max_length = 200, choices=STUDY_LEVEL_CHOICES, null=True, blank=True ,default='0')
    experience  = models.CharField(verbose_name = u'Experience', max_length = 200, choices=EXPERIENCE_CHOICES,  null=True, blank=True ,default='0')
    work_time   = models.CharField(_('temps de travail'), max_length = 200, null=True, blank=True)
    hiring_date = models.DateTimeField(_('date d\'embauche '), null=True, blank=True)

    views       = models.CharField(_('Nombre de vues'),max_length = 200, blank=True, default=0)
    description = models.TextField(_('description'), blank=True, null=True)

    created     = models.DateTimeField(_('date de creation'), null=True)
    modified    = models.DateTimeField(_('date de modification'), null=True)
    expired     = models.DateTimeField(_('date d\'expiartion '), null=True, blank=True)
    immediate   = models.CharField(max_length = 20, choices=YESNO, default='1')

    activated   = models.BooleanField(_('Activee'), blank=True, default=True)


    class Meta:
        verbose_name        = _('Offre')
        verbose_name_plural = _('Offres')

    def __unicode__(self):
        return unicode(self.title)

    objects = OfferManager() # to get only active: Offer.objects.is_watermaked

    @property
    def cache_key(self):
        return self.get_absolute_url()

    def is_available(self):
        day_count = (self.expired - self.created).days + 1
        return day_count >= 0

    def remaining_days(self):
        day_count = (self.expired - self.created).days + 1
        return day_count

    def get_applyers_count(self):
        return self.profile_candid_set.count()

    def head_summary(self):
        LIMIT = 80
        tail = len(self.description) > LIMIT and '......' or ''
        return self.description[:LIMIT] + tail

    def tooltip_head_summary(self):
        LIMIT = 280
        tail = len(self.description) > LIMIT and '......' or ''
        return self.description[:LIMIT] + tail

    def get_absolute_url(self): return '/offer/%s/' %(self.id)

    def get_disable_url(self): return '/offer/%s/disable' %(self.id)

    def get_unmark_url(self): return '/offer/%s/unmark' %(self.id)

    def get_activation_url(self): return '/offer/%s/activate' %(self.id)

    def get_edition_url(self): return '/offer/%s/edit' %(self.id)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id: self.created = datetime.datetime.today()
        self.modified = datetime.datetime.today()

        if not self.slug:
            self.slug = slugify(self.title)  # Where self.title is the field used for 'pre-populate from'

        while True:
            try:
                super(Offer, self).save()
            # Assuming the IntegrityError is due to a slug fight
            except IntegrityError:
                match_obj = re.match(r'^(.*)-(\d+)$', self.slug)
                if match_obj:
                    next_int = int(match_obj.group(2)) + 1
                    self.slug = match_obj.group(1) + '-' + str(next_int)
                else:
                    self.slug += '-2'
            else:
                break

        # ping google to update sitemap.xml
        try:
            ping_google()
        except Exception:
            pass

        return super(Offer, self).save(*args, **kwargs)

    # this a function for the image list display
    def image_tag(self):

        return u'<img src="%s" width="80" height="80" />' % self.image.url
        image_tag.short_description = 'Image'

    image_tag.allow_tags = True


    def get_company(self):
        return self.user.profile_emp

    def is_marked(self, *args):
        person, company = args
        marked = self.appreciation_set.filter(person = person , company = company)
        if len(marked) > 0:
            return True
        else: 
            return False

    def candid_intersection(self):

        candids = list(profile.models.Profile_candid.objects.all().order_by('-created_at'))
        di    = {}
        found = 0

        if self.slug:
            offer_tags = self.slug.split('-')
            for i in candids:
                if found == 6 :
                    break

                if i.wtd_job_slug:
                    slug        = i.wtd_job_slug
                    candid_tags = slug.split('-')
                    inter = set(offer_tags).intersection(candid_tags)
                    inter = len(list(inter))

                    if inter > 0:
                        found += 1
                        di[i] = range(inter)
                    else:
                        continue    

                else:
                    continue    

        else:
            return di    
        
        return di
        

# updating/deleting cache
post_save.connect(cache_update, sender=Offer)
post_delete.connect(cache_evict, sender=Offer)
