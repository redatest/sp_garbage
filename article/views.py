# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

# models and forms
from offre.models import Offer
from article.models import Article

# pagination and search
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from car_shop.model_choices import REGION_CHOICES, SALARY_CHOICES, CATEGORY_CHOICES, OFFER_CHOICES, YESNO
from django.db.models import F

# settings
from django.utils import translation


def news(request):
    # articles    = Article.objects.all()
    # paginator   = Paginator(articles, 3) 
    # page        = request.GET.get('page')

    # try: contacts = paginator.page(page)
    # except PageNotAnInteger:    contacts = paginator.page(1)
    # except EmptyPage:           contacts = paginator.page(paginator.num_pages)

    return render_to_response('articles/news.html', locals(), context_instance = RequestContext(request))

def news_item(request, num):
    article = Article.objects.get(id = num)
    return render_to_response('articles/news_item.html', locals(), context_instance = RequestContext(request))
