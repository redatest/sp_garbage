# -*- coding: utf-8 -*-
from django import forms
from car_shop.model_choices import *
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm



class Text_Search_Form(forms.Form):
	target_text     = forms.CharField(label= _("target text"), required=True, widget=forms.TextInput(attrs={'class':'form-control input-sm', 'name':'s'}))

class Search_Form(forms.Form):
	offer 			= forms.ChoiceField(label= _("Offre"), choices=OFFER_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	category 		= forms.ChoiceField(label= _("Categorie"), choices=CATEGORY_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	city 			= forms.ChoiceField(label= _("Departement"), choices=DEPARTEMENT_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	region 			= forms.ChoiceField(label= _("Region"), choices=REGION_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	experience 		= forms.ChoiceField(label= _("Experience"), choices=EXPERIENCE_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))
	study_level  	= forms.ChoiceField(label= _("Niveau"), choices=STUDY_LEVEL_CHOICES, widget=forms.Select(attrs={'class':'form-control input-sm'}))

