# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
import os
import sys

# models and forms
from offre.models import Offer
from offre.forms import OfferForm, EditOfferForm
from car_shop.forms import Search_Form, Text_Search_Form
from profile.models import Profile_candid, Profile_emp, Application, Appreciation
from profile.forms import UserInfoForm, EmployerInfoForm
# pagination and search
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from car_shop.model_choices import REGION_CHOICES, SALARY_CHOICES, CATEGORY_CHOICES, OFFER_CHOICES, YESNO
from django.db.models import F

# login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group

from django.core.mail import send_mail
from django.contrib import messages
from django.core.context_processors import csrf
from django.utils import translation

#email
from car_shop.nicemails import send_nice_email
from django.conf import settings
from django.contrib.sites.models import Site
import subprocess


# decorating , logging and caching
from utils.decorators import set_notification_message, restrict_candidate, restrict_employer
from django.core.cache import cache
import logging
from datetime import datetime

def get_real_profile(req):
    """ get user status from custom context process """
    return RequestContext(req).get('real_profile')

def offer(request, num):
    """ display offer """

    real_profile = get_real_profile(request)
    # offer_cache_key = "{}".format(request.path)
    # offer = cache.get(offer_cache_key)
    # if a cache miss, fall back on database query
    
    offer = Offer.objects.get( id = num )
    # store in cache for next time


    next        = offer.get_absolute_url()
    offer.views = int(offer.views)+1
    offer.save()

    can_edit        = False
    already_applyed = False

    if request.user.username == offer.user.username: can_edit = True

    if isinstance(real_profile, Profile_candid):
        already_applied = real_profile in offer.profile_candid_set.all()

    empo = real_profile    

    return render_to_response('offre/offer.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_employer
def offer_edit(request, num):
    """ edit offer by employer """

    car = Offer.objects.get(id = num)
    if request.user.username == car.user.username: can_edit = True

    if request.method == 'POST':
        form = EditOfferForm(request.POST, request.FILES)

        if form.is_valid():
            changed_fields = form.changed_data

            if 'title' in changed_fields:           title = form.cleaned_data['title']
            if 'category' in changed_fields:        category = form.cleaned_data['category']
            if 'offer' in changed_fields:           offer = form.cleaned_data['offer']
            if 'city' in changed_fields:            city = form.cleaned_data['city']
            if 'town' in changed_fields:            town = form.cleaned_data['town']
            if 'postal_code' in changed_fields:     postal_code = form.cleaned_data['postal_code']
            if 'study_level' in changed_fields:     study_level = form.cleaned_data['study_level']
            if 'experience' in changed_fields:      experience = form.cleaned_data['experience']
            if 'work_time' in changed_fields:       work_time = form.cleaned_data['work_time']
            if 'hiring_date' in changed_fields:     hiring_date = form.cleaned_data['hiring_date']
            if 'region' in changed_fields:          region = form.cleaned_data['region']
            if 'salary' in changed_fields:          salary = int(form.cleaned_data['salary'])
            if 'immediate' in changed_fields:       immediate = form.cleaned_data['immediate']
            if 'description' in changed_fields:     description = form.cleaned_data['description']
            if 'expired' in changed_fields:         expired = form.cleaned_data['expired']

            else:
                image = car.image

            car.title       = title
            car.offerType   = offer
            car.salary      = salary
            car.town        = town
            car.postal_code = postal_code
            car.study_level = study_level
            car.experience  = experience
            car.work_time   = work_time
            car.hiring_date = hiring_date
            car.city        = city
            car.region      = region
            car.category    = category
            car.immediate   = immediate
            car.description = description
            car.expired     = expired

            car.save()
            return HttpResponseRedirect(car.get_absolute_url())

        else:
            # to revise
            render_to_response('offre/offer_edit.html', locals(), context_instance = RequestContext(request))

    else:
        form = EditOfferForm(initial={  'title':        car.title,
                                        'category':     car.category,
                                        'salary':       car.salary,
                                        'town':         car.town,
                                        'postal_code':  car.postal_code,
                                        'city':         car.city,
                                        'region':       car.region,
                                        'offer':        car.offerType,
                                        'immediate':    car.immediate,
                                        'description':  car.description,
                                        'work_time':  car.work_time,
                                        'hiring_date':  car.hiring_date,
                                        'experience':  car.experience,
                                        'study_level':  car.study_level,
                                        'expired':      car.expired
                                        })

    return render_to_response('offre/offer_edit.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_candidate
def offer_mark(request, num):
    """ Mark offer as favoraite """

    offer   = get_object_or_404(Offer, id=num)
    company = offer.user.profile_emp
    person  = Profile_candid.objects.get(user = request.user)

    mark, created    = Appreciation.objects.get_or_create(offer=offer, person=person, company=company)
    mark.save()
    return HttpResponseRedirect('/candid_profile_marks')


@login_required
@restrict_candidate
def offer_unmark(request, num, comp):
    """ Unmark favoraite offer """

    offer   = Offer.objects.get(id=num)
    company = Profile_emp.objects.get(id = comp)
    person  = Profile_candid.objects.get(user = request.user)

    mark, created    = Appreciation.objects.get_or_create(offer=offer, person=person, company=company)

    mark.delete()

    return HttpResponseRedirect('/candid_profile_marks')


#  ~todo: make the call by ajax
@login_required
@restrict_employer
def offer_disable(request, num):
    """ deactivate offer """

    offer = get_object_or_404(Offer, id=num)
    offer.activated = False
    offer.save()
    return HttpResponseRedirect('/emp_profile_offres/')

# todo make the call by ajax
@login_required
@restrict_employer
def offer_activate(request, num):
    """ activate offer """

    offer = get_object_or_404(Offer, id=num)
    offer.activated = True
    offer.save()
    return HttpResponseRedirect("/emp_profile_offres/")

@login_required
@restrict_candidate
def offer_postulate(request, num):
    """ Apply to an offer """

    offer        = get_object_or_404(Offer, id=num)
    offer_title  = offer.title
    offer_date   = offer.created
    offer_region = offer.get_region_display()

    owner        = offer.user
    owner_name   = offer.user.username
    owner_email  = offer.user.email

    sender       = request.user
    sender_name  = request.user.username
    sender_email = request.user.email

    # log = logging.getLogger(__name__)

    static_files_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'static'))
    # get current website
    current_site = Site.objects.get_current()
    site_root    = current_site.domain
    full_offer_url = site_root +  offer.get_absolute_url()

    # get the candidate profile linked to this user
    applyer = sender.profile_candid
    entreprise = owner.profile_emp

    # test if sender has written some motivations
    if applyer.motivations == None or len(applyer.motivations) < 1:
        msg = 'Votre candidature n\'as pas été pris en compte .Veuillez exprimer un peu vos motivations sur la page de votre profile '
        url = reverse('offer', kwargs={'num': num})
        
        return render_to_response('offre/offer.html', locals(), context_instance = RequestContext(request))

    motivations = applyer.motivations

    if applyer in offer.profile_candid_set.all():
        msg = 'vous avez postulé pour l\'offre déja'

        url = reverse('offer', kwargs={'num': num})
        return render_to_response('offre/offer.html', locals(), context_instance = RequestContext(request))

    context = {
                'nom':              sender_email,
                'company':          owner_name,
                'titre':            offer_title,
                'lieu':             offer_region,
                'creattion_date':   offer_date
               }

    subject = ugettext(u"SpeedJob: Votre candidature pour %s") % (offer_title)

    application_message = u"""
        <br/>
        Nous vous confirmons l'envoi de votre candidature au recruteur.
        <br/>
        <br/>
        <br/>

        <img src='http://www.speedjob.fr/static/images/logo1_dark.png' />
        <br/>
        <br/>
        <br/>
        &nbsp;&nbsp;&nbsp; <a href='www.speejob.fr'>www.speedjob.fr</a>
        <br/>
        """

    try:
        sendmail = subprocess.Popen(
            [sys.executable,
            '/kunden/homepages/11/d445074125/htdocs/speedjob/car_shop/no_smtp.py', sender_email ,str(application_message) ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
            )

    except Exception, e:
        msg = 'L\'envoi de votre demande a échoué'
        return render_to_response('offre/offer.html', locals(), context_instance = RequestContext(request))

    # send a copy to the employer
    context = {
                 'nom':             owner_email,
                 'company':         owner_name,
                 'titre':           offer_title,
                 'lieu':            offer_region,
                 'creattion_date':  offer_date,
                 'is_active':       offer.activated,
                 'full_offer_url':  full_offer_url ,
                 'motivations'   :  motivations
                }

    subject = ugettext(u" Candidature sur SpeedJob ")

    application_message = """
        <br>
        Bonjour <strong> {1} </strong>
        <br>
        <br>
        Un candidat vient de postuler à l'annonce suivante: 
        <br>
        <a href="http://{0}">{0}</a>
        <br/>
        <br/>
        Veuillez consulter votre compte sur notre site
        <br/>
        <br/>
        Merci de votre confiance
        <br/>
        <br/>
        SpeedJob
        <br/>
        <br/>
        <img src='http://www.speedjob.fr/static/images/logo1_dark.png' />
        <br/>
        <br/>
        <br/>
        &nbsp;&nbsp;&nbsp; <a href='www.speedjob.fr'>www.speedjob.fr</a>
        <br/>
        """.format( full_offer_url, owner_name )

    try:
        sendmail = subprocess.Popen(
            [sys.executable,
            '/kunden/homepages/11/d445074125/htdocs/speedjob/car_shop/no_smtp_apply.py', owner_email ,str(application_message) ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
            )

    except Exception, e:
        msg = 'L\'envoi de votre demande a échoué'
        return render_to_response('offre/offer.html', locals(), context_instance = RequestContext(request))

    msg = 'Votre demande a été envoyé avec succès'

    # create an application that joins the candidate and the offer
    app = Application(offer=offer, person=applyer, company=entreprise )
    app.save()

    url = reverse('offer', kwargs={'num': num})
    return HttpResponseRedirect(url)


@login_required
@restrict_employer
def deposer_offre(request):
    """ deposite offer in the the website """

    form = Search_Form()

    if request.method == 'POST':

        offer_form = OfferForm(request.POST, request.FILES)

        if offer_form.is_valid():

            title            = offer_form.cleaned_data['title']
            offer            = offer_form.cleaned_data['offer']
            category         = offer_form.cleaned_data['category']
            town             = offer_form.cleaned_data['town']
            postal_code      = offer_form.cleaned_data['postal_code']
            city             = offer_form.cleaned_data['city']
            region           = offer_form.cleaned_data['region']
            study_level      = offer_form.cleaned_data['study_level']
            experience       = offer_form.cleaned_data['salary']
            salary           = offer_form.cleaned_data['salary']
            work_time        = offer_form.cleaned_data['work_time']
            hiring_date      = offer_form.cleaned_data['hiring_date']
            immediate        = offer_form.cleaned_data['immediate']
            expired          = offer_form.cleaned_data['expired']
            description      = offer_form.cleaned_data['description']
            # image           = request.FILES['image']
            newcar = Offer( title           = title,
                            offerType       = offer,
                            salary          = salary,
                            category        = category,
                            town            = town,
                            postal_code     = postal_code,
                            city            = city,
                            region          = region,
                            study_level     = study_level,
                            experience      = experience,
                            hiring_date     = hiring_date,
                            work_time       = work_time,
                            immediate       = immediate,
                            description     = description,
                            expired         = expired,
                            user            = request.user )
            newcar.save()

            profile = request.user
            last_offer = profile.offer_set.latest('created').id

            url = reverse('offer', kwargs={'num': last_offer})
            return HttpResponseRedirect(url)
            
        else:
            messages.add_message(request, messages.ERROR, ' SVP corrigez votre formulaire .')

    else:
        offer_form = OfferForm()
    return render_to_response('offre/deposer_offre.html', locals(), context_instance = RequestContext(request))


@login_required
@restrict_employer
def app_confirm(request, offer_id, user_id, app_id):
    """ confirm application """

    app = Application.objects.get(id = app_id)
    app.is_seen = True
    app.save()
    return HttpResponseRedirect('/applications')

@login_required
@restrict_employer
def app_reject(request, offer_id, user_id, app_id):
    """ reject application """

    app = Application.objects.get(id = app_id)
    app.is_seen = False
    app.save()
    return HttpResponseRedirect('/applications')


@login_required
@restrict_employer
def applications(request):
    """ display applications for employer """

    real_profile = get_real_profile(request)
    apps = Application.objects.filter(company = real_profile)
    
    return render_to_response('profile/profile_emp_applications.html', locals(), context_instance=RequestContext(request))


