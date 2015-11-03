#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_list_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse

# models and forms
from offre.models import Offer
from article.models import Article
from car_shop.forms import Search_Form, Text_Search_Form
from profile.models import Profile_candid, Profile_emp, Download
from profile.forms import UserInfoForm, EmployerInfoForm
# pagination and search
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from car_shop.model_choices import REGION_CHOICES, SALARY_CHOICES, CATEGORY_CHOICES, OFFER_CHOICES, YESNO

from django.conf import settings

# login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group


from django.core.mail import send_mail
from django.contrib import messages
from django.core.context_processors import csrf
from django.utils import translation

# caching
from django.views.decorators.cache import cache_page

import datetime
import os

# payments
import stripe
from payments.models import Customer, Charge

# decorators
from utils.decorators import set_notification_message, restrict_candidate, restrict_employer

## get user status from custom context process
def get_real_profile(req):
    return RequestContext(req).get('real_profile')

# make sure that the get paramas are numeric
def real_field(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

#@login_required
#@restrict_candidate
def search(request):

    real_profile = get_real_profile(request)
    text_form    = Text_Search_Form()
    form         = Search_Form()

    # preparing search words if we came from the index page
    
    if 'offer' in request.GET:  offer              = request.GET.get('offer')
    else: offer = None

    if 'category' in request.GET:  category        = request.GET.get('category')
    else: category    = None

    if 'city' in request.GET:  city                = request.GET.get('city')
    else: city       = None
        
    if 'region' in request.GET:  region            = request.GET.get('region')
    else: region      = None


    page        = request.GET.get('page')

    # in the normal display of the view
    if city        == None : city        = 'all'
    if region      == None : region      = 'all'
    if category    == None : category    = 'all'
    if offer       == None : offer       = 'all'

    offers          = Offer.objects.all().filter(activated=True).order_by('-created')

    if real_field(city)           :   offers = offers.filter(city          = city)
    if real_field(region)         :   offers = offers.filter(region        = region)
    if real_field(category)       :   offers = offers.filter(category       = category)
    if real_field(offer)          :   offers = offers.filter(offerType      = offer)

    articles    = offers
    paginator   = Paginator(articles, 9)
    page        = request.GET.get('page')
    query        = request.GET.get('city')

    srch_res = offers.count()

    try: contacts = paginator.page(page)
    except PageNotAnInteger: contacts = paginator.page(1)
    except EmptyPage: contacts = paginator.page(paginator.num_pages)

    if isinstance(real_profile, Profile_candid):
        empo = real_profile

    return render_to_response('./search/search.html' , locals(), context_instance = RequestContext(request))

@login_required
@restrict_employer
def search_emp(request):

    # preparing forms
    text_form   = Text_Search_Form()
    form        = Search_Form()


    u = request.user
    empo = get_real_profile(request)
    
    # preparing search words if we came from the index page

    if 'offer' in request.GET:  offer             = request.GET.get('offer')
    else: offer = None

    if 'category' in request.GET:  category       = request.GET.get('category')
    else: category    = None

    if 'city' in request.GET:  city               = request.GET.get('city')
    else: city       = None
        
    if 'region' in request.GET:  region           = request.GET.get('region')
    else: region      = None

    if 'study_level' in request.GET:  study_level = request.GET.get('study_level')
    else: study_level = None

    if 'experience' in request.GET:  experience   = request.GET.get('experience')
    else: experience    = None

    page        = request.GET.get('page')

    # in the normal display of the view
    if city        == None : city           = 'all'
    if region      == None : region         = 'all'
    if category    == None : category       = 'all'
    if offer       == None : offer          = 'all'
    if experience  == None : experience     = 'all'
    if study_level == None : study_level    = 'all'

    last_users     = Profile_candid.objects.all().order_by('-created_at')

    if real_field(city)               :   last_users = last_users.filter(city            = city)
    if real_field(region)             :   last_users = last_users.filter(region          = region)
    if real_field(category)           :   last_users = last_users.filter(sector1        = category)
    if real_field(offer)              :   last_users = last_users.filter(contract           = offer)
    if real_field(experience)         :   last_users = last_users.filter(experience      = experience)
    if real_field(study_level)        :   last_users = last_users.filter(study_level     = study_level)

    articles  = last_users
    paginator = Paginator(articles, 9)
    page      = request.GET.get('page')
    query     = request.GET.get('region')

    srch_res = last_users.count()

    try: contacts = paginator.page(page)
    except PageNotAnInteger: contacts = paginator.page(1)
    except EmptyPage: contacts = paginator.page(paginator.num_pages)

    return render_to_response('./search/search_emp.html' , locals(), context_instance = RequestContext(request))

#@login_required
#@restrict_candidate
def map_search(request):

    text_form   = Text_Search_Form()
    form        = Search_Form()

    if 'offer' in request.GET:  offer             = request.GET.get('offer')
    else: offer = None

    if 'category' in request.GET:  category       = request.GET.get('category')
    else: category    = None

    if 'city' in request.GET:  city               = request.GET.get('city')
    else: city       = None
        
    if 'region' in request.GET:  region           = request.GET.get('region')
    else: region      = None

    page        = request.GET.get('page','')

    # in the normal display of the view
    if city     == None : city      = 'all'
    if region   == None : region    = 'all'
    if category == None : category  = 'all'
    if offer    == None : offer     = 'all'

    offers          = Offer.objects.all().filter(activated=True).order_by('-created')

    if real_field(offer)          :   offers = offers.filter(offerType         = offer)
    if real_field(city)           :   offers = offers.filter(city          = city)
    if real_field(region)         :   offers = offers.filter(region        = region)
    if real_field(category)       :   offers = offers.filter(category      = category)
    

    articles  = offers
    paginator = Paginator(articles, 9)
    page      = request.GET.get('page')
    query     = request.GET.get('city')

    srch_res = offers.count()

    try: contacts                        = paginator.page(page)
    except PageNotAnInteger:    contacts = paginator.page(1)
    except EmptyPage:           contacts = paginator.page(paginator.num_pages)

    empo = get_real_profile(request)

    return render_to_response('./search/map_search.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_employer
def map_search_emp(request):

    
    text_form   = Text_Search_Form()
    form        = Search_Form()

    # preparing search words if we came from the index page

    if 'offer' in request.GET:  offer           = request.GET.get('offer')
    else: offer = None

    if 'category' in request.GET:  category     = request.GET.get('category')
    else: category    = None

    if 'city' in request.GET:  city             = request.GET.get('city')
    else: city       = None
        
    if 'region' in request.GET:  region         = request.GET.get('region')
    else: region      = None

    if 'experience' in request.GET:  experience           = request.GET.get('experience')
    else: experience   = None

    if 'study_level' in request.GET:  study_level         = request.GET.get('study_level')
    else: study_level  = None

    page        = request.GET.get('page')

    # in the normal display of the view
    if city        == None : city           = 'all'
    if region      == None : region         = 'all'
    if category    == None : category       = 'all'
    if offer       == None : offer          = 'all'
    if experience  == None : experience     = 'all'
    if study_level == None : study_level    = 'all'

    last_users      = Profile_candid.objects.all().order_by('-created_at')

    if real_field(city)               :   last_users = last_users.filter(city            = city)
    if real_field(region)             :   last_users = last_users.filter(region          = region)
    if real_field(category)           :   last_users = last_users.filter(sector1        = category)
    if real_field(offer)              :   last_users = last_users.filter(contract           = offer)
    if real_field(experience)         :   last_users = last_users.filter(experience      = experience)
    if real_field(study_level)        :   last_users = last_users.filter(study_level     = study_level)

    articles  = last_users
    paginator = Paginator(articles, 9)
    page      = request.GET.get('page')
    query     = request.GET.get('city')

    srch_res = last_users.count()

    try: contacts                        = paginator.page(page)
    except PageNotAnInteger:    contacts = paginator.page(1)
    except EmptyPage:           contacts = paginator.page(paginator.num_pages)

    empo = get_real_profile(request)
    
    return render_to_response('./search/map_search_emp.html', locals(), context_instance = RequestContext(request))

def get_pagination_page(page=1, items=None):

    items = Offer.objects.all().filter(activated=True)
    paginator = Paginator(items, 4)
    try: page = int(page)
    except ValueError: page = 1

    try:    items = paginator.page(page)
    except  (EmptyPage, InvalidPage): items = paginator.page(paginator.num_pages)

    return items

def land_page_pagination(page=1, items=None):
    
    items = items
    paginator = Paginator(items, 9)

    try:    page = int(page)
    except  ValueError: page = 1

    try:    items = paginator.page(page)
    except  (EmptyPage, InvalidPage): items = paginator.page(paginator.num_pages)

    return items


@login_required
@restrict_employer
def search_candidates(request):
    # preparing forms
    text_form   = Text_Search_Form()
    form        = Search_Form()

    users = Profile_candid.objects.all()

    articles  = users
    paginator = Paginator(articles, 15)
    page      = request.GET.get('page')
    #paginating found users
    try: contacts = paginator.page(page)
    except PageNotAnInteger:    contacts = paginator.page(1)
    except EmptyPage:           contacts = paginator.page(paginator.num_pages)
    return render_to_response('./profile/search_candidates.html', locals(), context_instance = RequestContext(request) )


@login_required
@restrict_employer
def search_auto(request):

    real_profile = get_real_profile(request)
    text_form    = Text_Search_Form()
    form         = Search_Form()
    offers       = real_profile.get_offers()
    empo         = get_real_profile(request)

    return render_to_response('./profile/search_auto.html', locals(), context_instance = RequestContext(request))


@login_required
@restrict_employer
def text_search_emp(request):

    real_profile = get_real_profile(request)
    text_form    = Text_Search_Form()
    form         = Search_Form()
    empo         = get_real_profile(request)

    if 'keyword' in request.GET:  
        wanted_job           = request.GET.get('keyword')
    else:
        wanted_job           = None

    if wanted_job     == None : wanted_job      = 'all'
    last_users        = Profile_candid.objects.all().order_by('-created_at')

    if wanted_job != "all"               :   last_users = last_users.filter(wanted_job__icontains = wanted_job)

    articles  = last_users
    paginator = Paginator(articles, 9)
    page      = request.GET.get('page')
    query     = request.GET.get('keyword')

    srch_res = last_users.count()

    try: contacts                        = paginator.page(page)
    except PageNotAnInteger:    contacts = paginator.page(1)
    except EmptyPage:           contacts = paginator.page(paginator.num_pages)

    return render_to_response('./search/search_emp.html', locals(), context_instance = RequestContext(request))


@login_required
@restrict_candidate
def text_search(request):

    real_profile = get_real_profile(request)
    text_form    = Text_Search_Form()
    form         = Search_Form()
    empo         = get_real_profile(request)


    if 'type_search' in request.GET:    type_search       = request.GET.get('type_search')
    else:                               type_search       = None

    if 'keyword' in request.GET:        keyword           = request.GET.get('keyword')
    else:                               keyword           = None

    if keyword         == None :        keyword           = 'all'

    offers          = Offer.objects.all().filter(activated=True).order_by('-created')

    if type_search:
        if type_search == 'title':
            offers = offers.filter(title__icontains = keyword)
        elif type_search == "description":
            offers = offers.filter(description__icontains = keyword)
                

    articles  = offers
    paginator = Paginator(articles, 9)
    page      = request.GET.get('page')
    query     = request.GET.get('keyword')

    srch_res = offers.count()

    try:   contacts                        = paginator.page(page)
    except PageNotAnInteger:    contacts = paginator.page(1)
    except EmptyPage:           contacts = paginator.page(paginator.num_pages)


    return render_to_response('./search/search.html', locals(), context_instance = RequestContext(request))
