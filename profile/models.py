# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, Group
from registration.signals import user_registered
from car_shop.model_choices import *

from offre.models import Offer
from profile.managers import profile_candid_manager
from payments.models import Customer
from django.db.models.signals import post_save
from django.dispatch import receiver

import subprocess
from django.conf import settings
from PyPDF2 import PdfFileReader, PdfFileWriter
import os
import uuid
import logging

# slugify title field
import re
from django.template.defaultfilters import slugify
import datetime
from django.contrib.sitemaps import ping_google

from django.db import IntegrityError
import hashlib

profile_type = ((True, 'Candidat'), (False, 'Recruteur') )

# high level user Model
class ExUserProfile(models.Model):
    user        = models.OneToOneField(User, unique=True, primary_key=True, db_index=True)
    is_candid   = models.BooleanField()

    def __unicode__(self):
        return unicode(self.user)


from django.utils.timezone import now as timezone_now
import os
def upload_dir(instance, filename):
    now = timezone_now()
    filename_base, filename_ext = os.path.splitext(filename)
    return 'uploads/logos/%s%s' % ( now.strftime("%Y/%m/%Y%m%d%H%M%S"), filename_ext.lower(), )


class Profile_emp(models.Model):
    user        = models.OneToOneField(User, unique=True, primary_key=True, db_index=True)
    is_candid   = models.BooleanField(default=False)

    class Meta:
        verbose_name        = "Employeur"
        verbose_name_plural = 'Emplyeurs'

    def __unicode__(self):
        return unicode(self.user)

    representant = models.CharField(max_length=230, null=True, blank=True)
    siret        = models.CharField(max_length=230, null=True, blank=True)
    created_at   = models.DateTimeField(verbose_name=u"Date de creation", auto_now_add = True, editable=False)
    society      = models.CharField(verbose_name=u"Société",     max_length=200, null=True, blank=True, default='')
    phone        = models.CharField(verbose_name=u"Téléphone",   max_length=200, null=True, blank=True, default='')
    address      = models.CharField(verbose_name=u'Adresse', max_length=200, null=True, blank=True, default="")
    postal_code  = models.CharField(verbose_name=u"Code postal", max_length=200, null=True, blank=True, default='')
    city         = models.CharField(verbose_name=u"Ville", max_length=200, null=True, blank=True)
    region       = models.CharField(verbose_name=u"Région", choices = REGION_CHOICES, max_length=200, null=True, blank=True, default='0')
    town         = models.CharField(verbose_name=u"Département",   choices = DEPARTEMENT_CHOICES,       max_length=200, null=True, blank=True, default='0')
    website      = models.CharField(verbose_name=u"Site Web",    max_length=200, null=True, blank=True, default='')
    presentation = models.TextField(verbose_name=u"Présentation",                null=True, blank=True, default='')

    logo         = models.ImageField(verbose_name = u'Logo', upload_to = upload_dir, null=True, blank=True)

    down_counter = models.IntegerField(blank=True, null=True, default = 0) 


    def __unicode__(self):
        return unicode(self.user)

    def get_absolute_url(self):
        return 'company/%s'%(self.user_id)     

    def get_payement_status(self):
        employer = self.user
        try:
            customer     = Customer.objects.get(user=employer)
            subscription = customer.current_subscription
            status       = subscription.status

        except Customer.DoesNotExist:
            return None

        return status

    def can_download(self):
        employer = self.user
        try:
            customer     = Customer.objects.get(user=employer)
            subscription = customer.current_subscription
            status       = subscription.status

            if status == "active":
                return True
            elif subscription.status == "canceled" and subscription.is_period_current():
                return True

        except Customer.DoesNotExist:
            return False

        return False

    def get_offers(self):
        offers = self.user.offer_set.all().order_by('-created')
        return offers

    def get_last_three_offers(self):
        offers = list(self.user.offer_set.all())[-3:]
        return offers    

    def get_all_fields(self):
        """Returns a list of all field names on the instance."""
        #log = logging.getLogger(__name__)
        #log.info("start of the test")

        fields = []
        for f in self._meta.fields:

            fname = f.name
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr( self, get_choice): value = getattr( self, get_choice)()
            else:
                try : value = getattr(self, fname)
                except User.DoesNotExist: value = None

            # only display fields with values and skip some fields entirely
            if f.editable and value and f.name not in ('id', 'user', 'is_candid', 'created_at', 'presentation') :
                fields.append( f.name )

        keys = ['society', 'phone', 'postal_code', 'town', 'region', 'website']
        msg  = None

        for i in keys:
            if not i in fields:
                msg = 'Votre profile est incomplet !!!'
                break
            else:
                continue
        return msg

    def is_there_non_confirmed_app(self):
        result = False
        for i in self.application_set.all():

              if not i.is_seen:
                    result = True
                    break

        return result

    def is_there_non_confirmed_alerts(self):
        result = False
        for i in self.alert_set.all():

              if not i.is_seen:
                    result = True
                    break

        return result    

    def has_been_watched(self,emp):
        
        return None

    def create_thumbnail(self, x, y):
        
        from PIL import Image
        from django.core.files.storage import default_storage as storage
        if not self.logo:
            return ""
        file_path = self.logo.name
        filename_base, filename_ext = os.path.splitext(file_path)
        thumbnail_file_path = "%s_thumbnail.jpg" % filename_base

        if storage.exists(thumbnail_file_path):
            # if thumbnail version exists, return its url path
            return "exists"
        try:    
            f = storage.open(file_path, 'r')
            image = Image.open(f)
            image.convert("RGBA") # Convert this to RGBA if possible

            width, height = image.size
            thumbnail_size = x, y

            if width > height:
                delta = width - height
                left = int(delta/2)
                upper = 0
                right = height + left
                lower = height
            else:
                delta = height - width
                left = 0
                upper = int(delta/2)
                right = width
                lower = width + upper

            # image = image.crop((left, upper, right, lower))
            image = image.resize(thumbnail_size, Image.ANTIALIAS)

            f_mob = storage.open(thumbnail_file_path, "w")
            image.save(f_mob, "JPEG")
            f_mob.close()
            return "success"
        except:
            return "error"


    def save(self, *args, **kwargs):
        super(Profile_emp, self).save(*args, **kwargs)
        # generate thumbnail picture version
        self.create_thumbnail(192,192)

    def get_thumbnail_picture_url(self):
        from django.core.files.storage import default_storage as storage
        if not self.logo:
            return ""
        file_path = self.logo.name
        filename_base, filename_ext = os.path.splitext(file_path)
        thumbnail_file_path = "%s_thumbnail.jpg" % filename_base
        if storage.exists(thumbnail_file_path):
            # if thumbnail version exists, return its url path
            return storage.url(thumbnail_file_path)
        # return original as a fallback
        return self.logo.url            


# remove accentuated characters from uploaded files CV
def update_filename(instance, filename):
    path = "upload/pdfs/"
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(path, filename)

class Profile_candid(models.Model):

    user          = models.OneToOneField(User, unique=True, primary_key=True, db_index=True)
    offer         = models.ManyToManyField(Offer, verbose_name="a postulé pour ",  null=True, blank=True, through = "Application" )

    is_candid     = models.BooleanField(default=True)

    wanted_job    = models.CharField(verbose_name = u'Poste voulu', max_length=500, null=True, blank=True,default="")
    wtd_job_slug  = models.CharField(verbose_name = u'Poste voulu decompose', max_length=250, blank=True, default='', editable=False)

    prenom        = models.CharField(max_length=230, null=True, blank=True,default="")

    last_name     = models.CharField(verbose_name = u'Nom de famille', max_length=200, null=True, blank=True, default="")
    created_at    = models.DateTimeField(verbose_name = u'Ajouté le', auto_now_add=True, null=True, blank=True, editable=False)
    adress        = models.CharField(verbose_name = u'Adresse', max_length=200, null=True, blank=True, default="")
    postal_code   = models.CharField(verbose_name = u'Code postal', max_length=200, null=True, blank=True, default="")
    town          = models.CharField(verbose_name = u"Ville", max_length=200, null=True, blank=True, default='', db_index=True)
    city          = models.CharField(verbose_name = u"Departement", choices = DEPARTEMENT_CHOICES, max_length=200, null=True, blank=True, default='0', db_index=True)
    region        = models.CharField(verbose_name = u"Région", choices = REGION_CHOICES, max_length=200, null=True, blank=True, default='0', db_index=True)

    telephone     = models.CharField(verbose_name = u'Telephone', max_length=200, null=True, blank=True)
    # recently added fields
    sector1       = models.CharField(verbose_name = u'Secteur 1', max_length = 200,choices=CATEGORY_CHOICES, null=True, blank=True, default='0')
    sector2       = models.CharField(verbose_name = u'Secteur 2', max_length = 200,choices=CATEGORY_CHOICES, null=True, blank=True,default='0')
    sector3       = models.CharField(verbose_name = u'Secteur 3', max_length = 200,choices=CATEGORY_CHOICES, null=True, blank=True, default='0')
    # mobility
    mobility1     = models.CharField(verbose_name = u'Mobilité 1', max_length = 200,choices=DEPARTEMENT_CHOICES, null=True, blank=True, default='0',db_index=True)
    mobility2     = models.CharField(verbose_name = u'Mobilité 2', max_length = 200,choices=DEPARTEMENT_CHOICES, null=True, blank=True, default='0')
    mobility3     = models.CharField(verbose_name = u'Mobilité 3', max_length = 200,choices=DEPARTEMENT_CHOICES, null=True, blank=True, default='0')

    disponibility = models.CharField(verbose_name = u'Disponibilité', max_length = 200,choices=DISPONIBILITY_CHOICES, null=True, blank=True, default='0')

    status        = models.CharField(verbose_name = u'Status', max_length = 200, choices=STATUS_CHOICES, null=True, blank=True ,default='0')
    salary        = models.CharField(verbose_name = u'Salaire', max_length = 200, choices=SALARY_CHOICES, null=True, blank=True ,default='0')

    study_level   = models.CharField(verbose_name = u'Niveau d\'etudes', max_length = 200, choices=STUDY_LEVEL_CHOICES, null=True, blank=True ,default='0')
    experience    = models.CharField(verbose_name = u'Experience', max_length = 200, choices=EXPERIENCE_CHOICES,  null=True, blank=True ,default='0')
    contract      = models.CharField(verbose_name = u'Contrat', max_length = 200, choices=OFFER_CHOICES, null=True,  blank=True,default='0')
    period        = models.CharField(verbose_name = u'periode', max_length = 200, choices=PERIOD_CHOICES, null=True, blank=True,default='0')

    languages     = models.CharField(verbose_name = u'langues', max_length=200, null=True, blank=True, default='')
    document      = models.FileField(verbose_name = u'Fichier PDF', upload_to = update_filename , null=True, blank=True)
    document_word = models.FileField(verbose_name = u'Fichier Word', upload_to = update_filename , null=True, blank=True)
    document_odt  = models.FileField(verbose_name = u'Fichier Open office', upload_to = update_filename , null=True, blank=True)
    
    motivations   = models.TextField(verbose_name = u'motivations',                null=True, blank=True ,default='')
    profess_exp   = models.TextField(verbose_name = u'Expèrience proffessionnelle',                null=True, blank=True,default='')
    certification = models.TextField(verbose_name = u'Formations',                null=True, blank=True ,default='')
    other_skills  = models.TextField(verbose_name = u'Compétences',                null=True, blank=True ,default='')
    
    views         = models.CharField(u'Nombre de vues',max_length = 200, blank=True, default=0)
    seen_by       = models.ManyToManyField(Profile_emp, verbose_name="vu par ",  null=True, blank=True, through = "Perception", editable=False )

    class Meta:
        verbose_name        = "Candidat"
        verbose_name_plural = 'Candidats'

    def __unicode__(self):
        return unicode(self.user)

    # override default object manager    
    objects = profile_candid_manager()    
    
    def get_full_name(self):
        """ Returns the first_name plus the last_name, with a space in between. """
        if len(self.prenom) == 0 and len(self.last_name) == 0 :
            return 'Mr %s' % (self.user.username)
        full_name = '%s-- %s-------' % (self.prenom[0], self.last_name[0])
	#full_name = '---- -------'
        return full_name.strip()

    def get_wanted_job(self):
        """ Returns the first_name plus the last_name, with a space in between. """
        if not self.wanted_job:
            return '%s' % ('Pas encore précisé sa demande')
        if len(self.wanted_job) < 1 or (self.wanted_job) == '' :
            return '%s' % ('Pas encore précisé sa demande')

        return self.wanted_job


    def get_salary_field(self):
        """ Returns the first_name plus the last_name, with a space in between. """
        if not self.salary:
            return '%s' % ('Pas encore déposé')
        if len(self.salary) < 1 or (self.salary) == '0' or (self.salary) == 'all' :
            return '%s' % ('Pas encore déposé')

        if (self.salary) == '1':
            return self.get_salary_display()

        return self.get_salary_display() + '<i class="fa fa-eur min-size"></i> '           

    def get_study_level_field(self):
        """ Returns the first_name plus the last_name, with a space in between. """
        if not self.study_level:
            return '%s' % ('Pas encore déposé')
        if len(self.study_level) < 1 or (self.study_level) == '0'  :
            return '%s' % ('Pas encore déposé')

        return self.get_study_level_display()

    def get_pdf_image(self):
        the_file = self.document.file.name.split('/')[-1].split('.')[0]
        return '%s/pdfs_images/img-%s.jpg' %( "/".join(self.document.file.name.split('/')[:-2] ), the_file)

    def get_absolute_url(self):
        return '/candidate/%s'%(self.user_id)

    def get_download_url(self):
        userinfo_id_hash = hashlib.md5(str(self.user_id).encode()).hexdigest()
        userinfo_down_url = userinfo_id_hash[16:] + str(self.user_id) + userinfo_id_hash[:16]
        return userinfo_down_url

    def has_uploaded_cv(self):
        return self.document.name or self.document_word.name or self.document_odt.name != ''
                

    def get_all_fields(self):
        """Returns a list of all field names on the instance."""
        fields = []
        for f in self._meta.fields:

            fname = f.name
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr( self, get_choice): value = getattr( self, get_choice)()
            else:
                try : value = getattr(self, fname)
                except User.DoesNotExist: value = None

            # only display fields with values and skip some fields entirely
            if f.editable and value and f.name not in ('user_id', 'workshop', 'user', 'complete', 'is_candid') :
                fields.append( f.name )

        keys = ['last_name', 
                'wanted_job', 
                'adress', 
                'town', 
                'city', 
                'region', 
                'telephone', 
                'sector1', 
                'sector2', 
                'sector3', 
                'mobility1', 
                'mobility2', 
                'mobility3', 
                'disponibility', 
                'status', 
                'salary', 
                'study_level', 
                'experience', 
                'contract', 
                'period', 
                'languages']

        msg  = None

        for i in keys:
            if not i in fields:
                msg = 'Votre profil est incomplet !!!'
                break
            else:
                continue
        return msg

    def has_been_watched(self,emp):
        # return 'seen or not seen'
        # return emp
        if self.perception_set.filter(employer = emp):
            return True
        else:
            return False

    # def save(self, *args, **kwargs):
        # self.wtd_job_slug = slugify(self.wanted_job)
        # try:
            # ping_google()
        # except Exception:
            # Bare 'except' because we could get a variety of HTTP-related exceptions.
            # pass
        # return super(Profile_candid, self).save(*args, **kwargs)

class Perception(models.Model):
    candid  = models.ForeignKey(Profile_candid, verbose_name="Candidate")
    employer= models.ForeignKey(Profile_emp, verbose_name="Employeur")
    # company = models.ForeignKey(Profile_emp, verbose_name="entreprise")
    created = models.DateTimeField(verbose_name= "date de la consultation", auto_now_add=True)
    is_seen = models.BooleanField(verbose_name='Vue', default=False)

    class Meta:
        verbose_name = 'Consultation'

    def __unicode__(self):
        return unicode(('Candidat: %s Employer: %s') %(self.candid.user.username, self.employer.user.username))

class Application(models.Model):
    offer   = models.ForeignKey(Offer, verbose_name="offre")
    person  = models.ForeignKey(Profile_candid, verbose_name="Candidat")
    company = models.ForeignKey(Profile_emp, verbose_name="entreprise")
    created = models.DateTimeField(verbose_name= "date de candidature", auto_now_add=True)
    is_seen = models.BooleanField(verbose_name='Vue', default=False)

    class Meta:
        verbose_name = 'candidature'

    def __unicode__(self):
        return unicode(('User: %s offer: %s') %(self.person.user.username, self.offer.title))

class Appreciation(models.Model):
    offer   = models.ForeignKey(Offer, verbose_name="offre")
    person  = models.ForeignKey(Profile_candid, verbose_name="Candidat")
    company = models.ForeignKey(Profile_emp, verbose_name="entreprise")
    created = models.DateTimeField(verbose_name= "date de d appreciation", auto_now_add=True)

    class Meta:
        verbose_name = 'appreciation'

    def __unicode__(self):
        return unicode(('User: %s offer: %s comapany: %s') %(self.person.user.username, self.offer.title, self.company))

class Alert(models.Model):
    person  = models.ForeignKey(Profile_candid, verbose_name="Candidat")
    company = models.ForeignKey(Profile_emp, verbose_name="Entreprise")
    created = models.DateTimeField(verbose_name= "date de d\'alerte", auto_now_add=True)
    is_seen = models.BooleanField(verbose_name='Vue', default=False)

    class Meta:
        verbose_name = 'Alerte'

    def __unicode__(self):
        return unicode(('Alerte: %s') %(self.id))


class Download(models.Model):
    
    person  = models.ForeignKey(Profile_candid, verbose_name="Candidat")
    company = models.ForeignKey(Profile_emp, verbose_name="entreprise")
    created = models.DateTimeField(verbose_name= "date de de telechargement", auto_now_add=True)

    class Meta:
        verbose_name = 'telechargement'

    def __unicode__(self):
        return unicode(('CV: %s entreprise: %s') %(self.person.user.username, self.company))


# def pdf_post_save(sender, instance=False, **kwargs):

#     pdf = instance

#     if pdf.document:
#         new_name =  pdf.document.file.name.split('/')[-1].split('.')[0]

#         output = PdfFileWriter()
#         pdfOne = PdfFileReader(file( '%s/%s' % (settings.MEDIA_ROOT, pdf.document), "rb"))
#         output.addPage(pdfOne.getPage(0))

#         outputStream = file(r'%s/uploads/first/%s-first.pdf'  % (settings.MEDIA_ROOT, new_name), "wb")
#         output.write(outputStream)
#         outputStream.close()

#         params = ['convert',
#                     '-blur' ,'4x6',
#                     (r'%s/uploads/first/%s-first.pdf')  % (settings.MEDIA_ROOT, new_name),
#                      '%s/uploads/pdfs_images/img-%s.jpg' % (settings.MEDIA_ROOT, new_name )
#                      ]
#         subprocess.check_call(params)

#     else:
#         pass    

# post_save.connect(pdf_post_save, sender=Profile_candid)


# this called after creation of the high level user
def user_registered_callback(sender, user, request, **kwargs):

    profile   = ExUserProfile(user = user)
    user_type = request.POST["is_candid"]
    if user_type == '1': profile.is_candid = True
    else:                profile.is_candid = False

    profile.save()

    if profile.is_candid :
        # get elementary information
        wanted_job    = request.POST.get('wanted_job', '')
        prenom        = request.POST.get('prenom', '')
        last_name     = request.POST.get('last_name', '')
        adress        = request.POST.get('adress', '')
        postal_code   = request.POST.get('postal_code', '')
        town          = request.POST.get('town', '')
        city          = request.POST.get('city', '')
        region        = request.POST.get('region', '')
        telephone     = request.POST.get('telephone', '')
        mobility1     = request.POST.get('mobility1', '') 
        sector1       = request.POST.get('sector1', '')
        salary        = request.POST.get('salary', '')
        contract      = request.POST.get('contract', '')
        disponibility = request.POST.get('disponibility', '')
        status        = request.POST.get('status', '')
        study_level   = request.POST.get('study_level', '')
        experience    = request.POST.get('experience', '')
        languages     = request.POST.get('languages', '')

        if "document" in request.FILES:
            document      = request.FILES.get('document', '')
        else:
            document = None  

        if "document_word" in request.FILES:
            document_word = request.FILES.get('document_word', '')
        else:
            document_word = None    

        if "document_odt" in request.FILES:
            document_odt = request.FILES.get('document_odt', '')
        else:
            document_odt = None    

        c  = Profile_candid(user            = user, 
                            is_candid       =True, 
                            wanted_job      = wanted_job, 
                            prenom          = prenom, 
                            last_name       = last_name, 
                            adress          = adress, 
                            postal_code     = postal_code, 
                            town            = town, 
                            city            = city, 
                            region          = region, 
                            telephone       = telephone, 
                            mobility1       = mobility1, 
                            sector1         = sector1, 
                            salary          = salary, 
                            contract        = contract, 
                            disponibility   = disponibility, 
                            status          = status, 
                            study_level     = study_level, 
                            experience      = experience, 
                            languages       = languages, 
                            document        = document, 
                            document_word   = document_word, 
                            document_odt    = document_odt )
        #add user to candidate group
        gr = Group.objects.get(name='candidate')
        gr.user_set.add(user)

        c.save()

    else:
        # get elementary information
        representant = request.POST.get('representant', '')
        siret        = request.POST.get('siret', '')
        phone        = request.POST.get('phone', '')
        address      = request.POST.get('address', '')
        city         = request.POST.get('city', '')
        postal_code  = request.POST.get('postal_code', '')
        town         = request.POST.get('town', '')
        website      = request.POST.get('website', '')
        region       = request.POST.get('region', '')

        c  = Profile_emp(user = user, 
                        is_candid    = False, 
                        society      = user.username, 
                        representant = representant, 
                        siret        = siret, 
                        address      = address, 
                        phone        = phone, 
                        postal_code  = postal_code, 
                        city         = city, 
                        town         = town, 
                        website      = website ,
                        region       = region)

        # add user to employer group
        gr = Group.objects.get(name='employer')
        gr.user_set.add(user)
        c.save()

user_registered.connect(user_registered_callback)
