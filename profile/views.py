# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

# models and forms
from offre.models import Offer
from article.models import Article
from car_shop.forms import Search_Form, Text_Search_Form
from profile.models import Profile_candid, Profile_emp, Application, Perception, Appreciation, Download, Alert
from profile.forms import UserInfoForm, EmployerInfoForm

# pagination ans search
from django.db.models import F
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger

# login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from utils.decorators import set_notification_message, restrict_candidate, restrict_employer

#utils
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from itertools import chain        


from django.core.context_processors import csrf
from django.utils import translation
import logging
import hashlib


def get_real_profile(req):
    """ get user status from custom context process """
    return RequestContext(req).get('real_profile')


@login_required
def profile_login(request):
    person             = get_real_profile(request)
    if person.is_candid:
        return HttpResponseRedirect('/candid_profile')
    else:
        return HttpResponseRedirect('/emp_profile')

@set_notification_message
@login_required
@restrict_candidate
def candid_profile(request,msg, profile):
    """ display candidate's profile  """

    person             = get_real_profile(request)
    appreciation_count = Appreciation.objects.filter(person = person).count()
    application_count  = Application.objects.filter(person = person).count()
    alerts_count       = Alert.objects.filter(person = person).count()

    if request.method == 'POST':
        
        form 	= UserInfoForm(data=request.POST,  user=request.user)
        if form.is_valid():
            form.save()
            message = messages.add_message(request, messages.INFO, 'données enregistrées avec succée')
            return HttpResponseRedirect('/profile/')
        else:
            message = messages.add_message(request, messages.INFO, 'erreur durant la savegarde  ')
            return render_to_response('profile.html', locals(), context_instance=RequestContext(request))

    else:
        form = UserInfoForm(user=request.user)
        userinfo = person
        return render_to_response('./profile/profile.html', locals(), context_instance=RequestContext(request))


@login_required
@restrict_candidate
def candid_profile_edit(request, id):
    """ edit candidate's profile """

    userinfo = get_real_profile(request)
    if request.method=='POST':
        form = UserInfoForm(request.POST, request.FILES)

        if form.is_valid():
            userinfo.wanted_job    = form.cleaned_data['wanted_job']
            userinfo.prenom        = form.cleaned_data['prenom']
            userinfo.adress        = form.cleaned_data['adress']
            userinfo.postal_code   = form.cleaned_data['postal_code']
            userinfo.town          = form.cleaned_data['town']
            userinfo.city          = form.cleaned_data['city']
            userinfo.region        = form.cleaned_data['region']
            userinfo.last_name     = form.cleaned_data['last_name']
            userinfo.telephone     = form.cleaned_data['telephone']
            userinfo.sector1       = form.cleaned_data['sector1']
            userinfo.sector2       = form.cleaned_data['sector2']
            userinfo.sector3       = form.cleaned_data['sector3']
            userinfo.mobility1     = form.cleaned_data['mobility1']
            userinfo.mobility2     = form.cleaned_data['mobility2']
            userinfo.mobility3     = form.cleaned_data['mobility3']
            userinfo.disponibility = form.cleaned_data['disponibility']
            userinfo.status        = form.cleaned_data['status']
            userinfo.salary        = form.cleaned_data['salary']
            userinfo.study_level   = form.cleaned_data['study_level']
            userinfo.experience    = form.cleaned_data['experience']
            userinfo.contract      = form.cleaned_data['contract']
            userinfo.period        = form.cleaned_data['period']
            userinfo.languages     = form.cleaned_data['languages']
            userinfo.motivations   = form.cleaned_data['motivations']
            userinfo.certification = form.cleaned_data['certification']
            userinfo.other_skills  = form.cleaned_data['other_skills']
            userinfo.profess_exp   = form.cleaned_data['profess_exp']

            changed_fields = form.changed_data


            if "document" in changed_fields: 
                userinfo.document           = form.cleaned_data['document']
            else: 
                userinfo.document = userinfo.document

            if "document_word" in changed_fields:
                userinfo.document_word = form.cleaned_data['document_word']
            else: 
                userinfo.document_word = userinfo.document_word

            if "document_odt" in changed_fields: 
                userinfo.document_odt   = form.cleaned_data['document_odt']
            else: 
                userinfo.document_odt = userinfo.document_odt

            # f = UserInfoForm.save(form)  # make the profile saving based on Candid_profile form
            userinfo.save()

        else:
            return render_to_response('./profile/profile_edit.html', locals(), context_instance = RequestContext(request))

        return HttpResponseRedirect('/candid_profile')
    else:
        form = UserInfoForm(initial = {
                            'wanted_job'    : userinfo.wanted_job,
                            'prenom'        : userinfo.prenom,
                            'adress'        : userinfo.adress,
                            'postal_code'   : userinfo.postal_code,
                            'town'          : userinfo.town,
                            'city'          : userinfo.city,
                            'region'        : userinfo.region,
                            'last_name'     : userinfo.last_name,
                            'telephone'     : userinfo.telephone,
                            'sector1'       : userinfo.sector1,
                            'sector2'       : userinfo.sector2,
                            'sector3'       : userinfo.sector3,
                            'mobility1'     : userinfo.mobility1,
                            'mobility2'     : userinfo.mobility2,
                            'mobility3'     : userinfo.mobility3,
                            'disponibility' : userinfo.disponibility,
                            'status'        : userinfo.status,
                            'salary'        : userinfo.salary,
                            'study_level'   : userinfo.study_level,
                            'experience'    : userinfo.experience,
                            'contract'      : userinfo.contract,
                            'period'        : userinfo.period,
                            'languages'     : userinfo.languages,
                            'document'      : userinfo.document,
                            'document_word' : userinfo.document_word,
                            'document_odt'  : userinfo.document_odt,
                            'motivations'   : userinfo.motivations,
                            'certification' : userinfo.certification,
                            'other_skills'  : userinfo.other_skills,
                            'profess_exp'   : userinfo.profess_exp
            })
    return render_to_response('./profile/profile_edit.html', locals(), context_instance = RequestContext(request))


@login_required
@restrict_employer
def emp_profile_edit(request, id):
    """ edit employer's profile """

    userinfo  = get_real_profile(request)

    if request.method=='POST':
        form = EmployerInfoForm(request.POST, request.FILES)

        if form.is_valid():

            # process the file first
            changed_fields = form.changed_data
            log = logging.getLogger(__name__)
            log.info('changed fields')
            log.info(changed_fields)
            log.info(form.cleaned_data['logo'])
            if 'logo' in changed_fields:
                logo = form.cleaned_data['logo']
            else:
                logo = userinfo.logo

            userinfo.representant = form.cleaned_data['representant']
            userinfo.siret        = form.cleaned_data['siret']
            userinfo.phone        = form.cleaned_data['phone']
            userinfo.postal_code  = form.cleaned_data['postal_code']
            userinfo.address      = form.cleaned_data['address']
            userinfo.city         = form.cleaned_data['city']
            userinfo.town         = form.cleaned_data['town']
            userinfo.region       = form.cleaned_data['region']
            userinfo.website      = form.cleaned_data['website']
            userinfo.logo         = logo
            userinfo.presentation = form.cleaned_data['presentation']
            userinfo.save()

        else:
            return render_to_response('./profile/profile_emp_edit.html', locals(), context_instance = RequestContext(request))

        return HttpResponseRedirect('/emp_profile')
    else:
        form = EmployerInfoForm(initial = {
                            'representant'      : userinfo.representant,
                            'siret'             : userinfo.siret,
                            'phone'             : userinfo.phone,
                            'postal_code'       : userinfo.postal_code,
                            'address'           : userinfo.address,
                            'town'              : userinfo.town,
                            'city'              : userinfo.city,
                            'region'            : userinfo.region,
                            'website'           : userinfo.website,
                            'presentation'      : userinfo.presentation,
                            'logo'              : userinfo.logo

            })
    return render_to_response('./profile/profile_emp_edit.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_employer
def emp_profile(request):
    """ display employer's profile """
    
    userinfo          = get_real_profile(request)
    offers_count      = userinfo.get_offers().count()
    application_count = Application.objects.filter(company = userinfo).count()
    alerts_count      = Alert.objects.filter(company = userinfo).count()

    if request.method == 'POST':
        
        form = Profile_emp(data=request.POST,  user=request.user)
        if form.is_valid():
            form.save()
            message = messages.add_message(request, messages.INFO, 'données enregistrées avec succée')
            return HttpResponseRedirect('/profile/')
        else:
            message = messages.add_message(request, messages.INFO, 'erreur durant la savegarde  ')
            return render_to_response('./profile/profile.html', locals(), context_instance=RequestContext(request))
    else:
        form = EmployerInfoForm(user=request.user)
        return render_to_response('./profile/profile_emp.html', locals(), context_instance=RequestContext(request))



@login_required
@restrict_candidate
def send_alert(request, id):
    """ Alerting an employer by actual candiate """
    userinfo       = Profile_emp.objects.get(user_id = id)
    candiate       = get_real_profile(request)
    company        = userinfo
    alert, created = Alert.objects.get_or_create(person=candiate, company=company)
    alert.save()

    url = reverse('company', kwargs={'num': id})
    # print url
    return HttpResponseRedirect(url)



@login_required
@restrict_candidate
def company(request, num):
    """ display specified employer's profile """
    
    has_alerted       = False  
    candiate          = get_real_profile(request)
    userinfo          = Profile_emp.objects.get(user_id = num)

    # we use iterator to optimize queryset searching
    alerts_iterator = candiate.alert_set.all().iterator()         

    try:
        first_atom = next(alerts_iterator)
    except StopIteration:
        # No rows were found, so do nothing.
        pass
    else:
        # At least one row was found, so iterate over, all the rows, including the first one.
        for y in chain([first_atom], alerts_iterator):
            # test if candiate has alerted the company
            if userinfo == y.company:
                has_alerted = True
                break

    # leave the post method may be it weill be used later
    if request.method == 'POST':
        
        form = Profile_emp(data=request.POST,  user=request.user)
        if form.is_valid():
            form.save()
            message = messages.add_message(request, messages.INFO, 'données enregistrées avec succée')
            return HttpResponseRedirect('/profile/')
        else:
            message = messages.add_message(request, messages.INFO, 'erreur durant la savegarde  ')
            return render_to_response('./profile/profile.html', locals(), context_instance=RequestContext(request))
    else:
        form = EmployerInfoForm(user=request.user)
        return render_to_response('./profile/company.html', locals(), context_instance=RequestContext(request))

@login_required
@restrict_employer
def emp_profile_offres(request):
    """ display offers posted by the employer """

    usname      = request.user.username
    uslname     = request.user.last_name
    userinfo    = get_real_profile(request)
    offers      = userinfo.get_offers().order_by('-created')
    return render_to_response('./profile/profile_emp_offers.html', locals(), context_instance=RequestContext(request))


@login_required
@restrict_employer
def emp_profile_alerts(request):
    """ display employer's profile """
    
    userinfo     = get_real_profile(request)
    offers_count = userinfo.get_offers().count()
    alerts_count = Alert.objects.filter(company = userinfo).count()
    apps         = Alert.objects.filter(company = userinfo)

    return render_to_response('./profile/profile_emp_alerts.html', locals(), context_instance=RequestContext(request))

@login_required
@restrict_employer
def alert_confirm(request, user_id, app_id):
    """ confirm Alert """

    app = Alert.objects.get(id = app_id)
    app.is_seen = True
    app.save()
    return HttpResponseRedirect('/emp_profile_alerts')

@login_required
@restrict_employer
def alert_reject(request, user_id, app_id):
    """ reject Alert """

    app = Alert.objects.get(id = app_id)
    app.is_seen = False
    app.save()
    return HttpResponseRedirect('/emp_profile_alerts')




@login_required
@restrict_employer
def emp_profile_offer_applyers(request, id):
    """ display applyers to employer's offers """

    offer       = Offer.objects.get(id=id)
    applyers    = offer.profile_candid_set.all()

    usname      = request.user.username
    uslname     = request.user.last_name
    userinfo    = get_real_profile(request)
    appli       = userinfo.application_set.filter(offer=offer)

    return render_to_response('./profile/profile_emp_offer_applyers.html', locals(), context_instance=RequestContext(request))

@login_required
@restrict_candidate
def candid_profile_marks(request):
    """ display offers marked by candidate """

    profile     = get_real_profile(request)
    usname      = request.user.username
    marks       = Appreciation.objects.filter(person = profile)

    return render_to_response('./profile/profile_candid_marks.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_candidate
def candid_profile_alerts(request):
    """ display alerts triggered by candidate """

    profile      = get_real_profile(request)
    usname       = request.user.username
    alerts       = Alert.objects.filter(person = profile)
    alerts_count = Alert.objects.filter(person = profile).count()
    marks       =  Alert.objects.filter(person = profile)

    return render_to_response('./profile/profile_candid_alerts.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_candidate
def candid_profile_application_status(request):

    usname      = request.user.username
    uslname     = request.user.last_name
    userinfo    = get_real_profile(request)
    appli       = userinfo.application_set.filter(person = userinfo)

    return render_to_response('./profile/candid_profile_application_status.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_employer
def candidate(request, num):

    real_profile = get_real_profile(request)
    candid       = Profile_candid.objects.get(user_id=num)
    candid.views = int(candid.views)+1
    candid.save()
    userinfo     = candid

    already_downloaded = False
    
    for i in userinfo.download_set.all():
        if real_profile == i.company:
            already_downloaded = True
            break

    doc = None

    if not Perception.objects.filter( employer = real_profile, candid = candid ):
        consultation = Perception(candid = candid, employer = real_profile, is_seen = True )
        consultation.save()

    return render_to_response('./profile/free_candidate.html', locals(), context_instance=RequestContext(request))


@login_required
@restrict_employer
def delete_profile_emp(request):
    u = request.user
    u.delete()
    return HttpResponseRedirect('/')

@login_required
@restrict_candidate
def delete_profile_candid(request):
    u = request.user
    u.delete()
    return HttpResponseRedirect('/')

@login_required
@restrict_candidate
def delete_candid_page(request):
    return render_to_response('./profile/delete_profile_candid.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_employer
def delete_emp_page(request):
    return render_to_response('./profile/delete_profile_emp.html', locals(), context_instance = RequestContext(request))

@login_required
@restrict_employer
def charge(request, num):
    """ display download page and decrease download counter """

    employer = get_real_profile(request)
    
    # this comes from a non pro employer
    if request.method == 'POST':
        form = request.POST

        # decrypt the url    
        the_id = num.replace(num[:16], '')  
        the_id = the_id[::-1] 
        the_id = the_id.replace(the_id[:16], '')
        the_id = the_id[::-1] 

        try:
            userinfo      =  Profile_candid.objects.get(user_id = the_id)
            return render_to_response('charge_process.html', locals(), context_instance=RequestContext(request))

        except Exception, e:
            return render_to_response('charge_process.html', locals(), context_instance=RequestContext(request))
        
    else:
        # this comes from a pro employer
        the_id = num.replace(num[:16], '')  
        the_id = the_id[::-1] 
        the_id = the_id.replace(the_id[:16], '')
        the_id = the_id[::-1] 

        try:
            userinfo     = Profile_candid.objects.get(user_id = the_id)
            obj, created = Download.objects.get_or_create( person = userinfo, company = employer )

            if created:
                obj.save() #record the download
                dc                    = (employer.down_counter) 
                employer.down_counter = (employer.down_counter) - 1 # decrease the employer download counter 
                employer.save()
            else:
                pass     
                
            remaining_downloads = employer.down_counter
            if remaining_downloads == 0:
                try:
                    customer     = Customer.objects.get(user=request.user)
                    customer.purge()
                except Exception, e:
                    pass

            return render_to_response('charge_process.html', locals(), context_instance=RequestContext(request))

        except Exception, e:
            
            return render_to_response('charge_process.html', locals(), context_instance=RequestContext(request))

    return render_to_response('charge_process.html', locals(), context_instance=RequestContext(request))





### todo : delete the subscription completely instead of just purging the customer
# subscription = customer.current_subscription
# subscritpion.delete()
# delete employer from customers list



