# -*- coding: utf-8 -*-
from django.db import models
from article.fields import ThumbnailImageField 
from car_shop.model_choices import *
import datetime
import math
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class Article(models.Model):

    title           = models.CharField(blank=True, max_length=200)
    summary         = models.TextField()
    body            = models.TextField()
    created         = models.DateTimeField(default=datetime.datetime.now)
    is_watermarked  = models.BooleanField(default=False)
    img             = ThumbnailImageField(upload_to='photos', blank=True, help_text = "for better resolution image size must be 600x280")
    image_title     = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['created']
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __unicode__(self): return self.title

    def get_absolute_url(self): return '/news_item/%s' % self.id

