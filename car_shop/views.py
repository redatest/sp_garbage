#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_list_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

# models and forms
from offre.models import Offer
from article.models import Article
from car_shop.forms import Search_Form, Text_Search_Form
from profile.models import Profile_candid, Profile_emp, Download
from profile.forms import UserInfoForm, EmployerInfoForm
# pagination and search
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from model_choices import REGION_CHOICES, SALARY_CHOICES, CATEGORY_CHOICES, OFFER_CHOICES, YESNO
from django.db.models import F
from django.conf import settings

# login
from django.contrib.auth.decorators import login_required, user_passes_test
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

@set_notification_message
def home(request, msg, profile):

    real_profile = get_real_profile(request)
    offers = Offer.objects.index_is_activated

    form                  = Search_Form()
    text_form             = Text_Search_Form()
    im_offers             = Offer.objects.all().filter(activated=True, immediate='Yes')
    last_im_offers        = []

    for i in im_offers:
        try:
            p = i.user.customer
            last_im_offers.append(i)
        except Exception, e:
            pass

    last_im_offers = last_im_offers[:3]
    if len(last_im_offers) < 3:
        last_im_offers = None

    # last subscribed users
    yesterday    = datetime.date.today() - datetime.timedelta(days=0)
    today_offers = Offer.objects.filter(created__gt=yesterday).count()
    today_users  = Profile_candid.objects.filter(created_at__gt=yesterday).count()
    last_users   = list(Profile_candid.objects.all().order_by('-created_at'))[:6]

    # last subscribed user near by employer
    if isinstance(real_profile, Profile_emp):
        employer        = real_profile
        employer_region = employer.region
        nearby_candids  = list(Profile_candid.objects.filter(region = employer_region))[-3:]

        IDF_offers_count      = Profile_candid.objects.idf_candidates_count
        MIDI_offers_count     = Profile_candid.objects.midi_candidates_count
        PACA_offers_count     = Profile_candid.objects.paca_candidates_count
        CALAIS_offers_count   = Profile_candid.objects.calais_candidates_count
        BRETAGNE_offers_count = Profile_candid.objects.idf_candidates_count

    empo = profile
    return render_to_response('index.html', locals(), context_instance = RequestContext(request))

def legales(request):
    return render_to_response('legales.html', locals(), context_instance=RequestContext(request))

def conditions(request):
    return render_to_response('conditions.html', locals(), context_instance=RequestContext(request))

def utilisation(request):
    return render_to_response('utilisation.html', locals(), context_instance=RequestContext(request))


def contact(request):
    errors = []
    if request.method == 'POST':

        if not request.POST.get('name', ''): errors.append('Enter a name')
        if not request.POST.get('subject', ''): errors.append('Enter a subject.')
        if not request.POST.get('message', ''): errors.append('Enter a message.')
        if request.POST.get('email') and '@' not in request.POST['email']: errors.append('Enter a valid e-mail address.')
        # create a model to just save contact messages tickets
        if not errors:
            try:
                send_mail(
                    #subject
                    request.POST['subject'],
                    #message
                    request.POST['message'],
                    # from
                    request.POST.get('email'),
                    # To [recipient list]
                    ['redatest7@gmail.com'],
                )
                messages.add_message(request, messages.INFO, 'message sent successflully.')
                return HttpResponseRedirect('/contact')
            except Exception, err:
                messages.add_message(request, messages.INFO, 'there was an error when processing your request.')
                return render_to_response('contact.html', locals(), context_instance = RequestContext(request))

    return render_to_response('contact.html', locals(), context_instance = RequestContext(request))

