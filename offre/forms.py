# -*- coding: utf-8 -*-
from django import forms
from car_shop.model_choices import *

from django.utils.translation import ugettext_lazy as _
import datetime
from django.contrib.admin import widgets



class OfferForm(forms.Form):
	
	title 			= forms.CharField(label=_("titre"), required=True, widget=forms.TextInput(attrs={'class':'form-control ', 'placeholder':'Soyez le plus précis possible'}))
	offer 			= forms.ChoiceField(label=_("Offre"), choices=OFFER_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	category	 	= forms.ChoiceField(label=_("Categorie"), choices=CATEGORY_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	town 			= forms.CharField(label=_("Ville"),  widget=forms.TextInput(attrs={'class':'form-control ', 'placeholder':'Ville'}))
	postal_code		= forms.CharField(label=_("Code postal"),  widget=forms.TextInput(attrs={'class':'form-control ', 'placeholder':'Code postal'}))
	city 			= forms.ChoiceField(label="Département", choices=DEPARTEMENT_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	region 			= forms.ChoiceField(label="Region", choices=REGION_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	study_level		= forms.ChoiceField(label="Niveau d\'études", choices=STUDY_LEVEL_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	experience		= forms.ChoiceField(label="Experience", choices=EXPERIENCE_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	work_time		= forms.CharField(label=_("Temps de travail"),  widget=forms.TextInput(attrs={'class':'form-control ', 'placeholder':'Plein temps / Temps partiel ....'}))
	hiring_date		= forms.CharField(label=_("Date d\'embauche"), min_length = 10, widget = forms.DateInput(format="%d-%m-%Y"))
	salary 			= forms.ChoiceField(label=_("Salaire"), choices=SALARY_CHOICES, widget=forms.Select(attrs={'class':'form-control'}))
	description 	= forms.CharField(label=_("description"), required=False, widget=forms.Textarea(attrs={'class':'form-control ', 'placeholder':'Decrivez votre annonce '}))
	immediate 		= forms.ChoiceField(label= _("immédiat"), required=False ,choices=YESNO, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	expired  		= forms.CharField(label=_("date d\'expiration"), min_length = 10, widget = forms.DateInput(format="%d-%m-%Y"))

	def clean_hiring_date(self):
		hiring_date = self.cleaned_data.get('hiring_date')    
		if hiring_date:    
			try:    
				hiring_date = datetime.datetime.strptime(hiring_date, '%d-%m-%Y')   
			except ValueError, e:    
				hiring_date = None    
				self._errors['hiring_date'] = 'La date choisie est invalide.'
			    
		return hiring_date

	def clean_expired(self):
		expired = self.cleaned_data.get('expired')    
		if expired:    
			try:    
				expired = datetime.datetime.strptime(expired, '%d-%m-%Y')    
			except ValueError:    
				expired = None    
				self._errors['expired'] = 'La date choisie est invalide.'
			    
		return expired 

	
class EditOfferForm(OfferForm):
	image = forms.FileField(label='Choisissez votre image', required=False, help_text='upload your photo')
	
	def __init__(self, *args, **kwargs):
		super(EditOfferForm, self).__init__(*args, **kwargs)
		self.fields["image"].widget.attrs.update({"class":"input-sm"})

