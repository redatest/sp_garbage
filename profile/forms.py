# -*- coding: utf-8 -*-
from registration.forms import RegistrationForm
from django import forms
from profile.models import Profile_candid, Profile_emp
 
profile_type = (('1', 'Candidat'), ('0', 'Recruteur') )

# this is just for the temporary user
class ExRegistrationForm(RegistrationForm):
    is_candid = forms.ChoiceField(label="Vous êtes :", choices=profile_type, required=True, widget=forms.RadioSelect())


# this my real profiles
class UserInfoForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(UserInfoForm, self).__init__(*args, **kwargs)
		for x in self.fields: self.fields[x].widget.attrs['class'] = 'form-control'
		for x in self.fields: self.fields[x].widget.attrs['style'] = 'margin-bottom:15px'


	def save(self, *args, **kwargs):
		instance = super(UserInfoForm, self).save(commit=False)
		# print '####################" the profile was saved'
		return instance.save()	

	class Meta:
		model 		= Profile_candid
		exclude 	= [ 'id', 'user', 'offer', 'is_candid', 'views'] 
		# exclude 	= [ 'id', 'user', 'offer', 'is_candid', 'document','document_word', 'document_odt']

	    	 

class EmployerInfoForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(EmployerInfoForm, self).__init__(*args, **kwargs)
		for x in self.fields: self.fields[x].widget.attrs['class'] = 'form-control'
		for x in self.fields: self.fields[x].widget.attrs['style'] = 'margin-bottom:15px'

		self.fields['presentation'].widget.attrs['style'] = 'margin-bottom:15px; background:#FAFBFB;'

	def save(self, *args, **kwargs):
		instance = super(EmployerInfoForm, self).save(commit=False)
		return instance.save()	

	class Meta:
		model 		= Profile_emp
		exclude 	= [ 'id', 'user', 'is_candid', 'society', 'down_counter'] 


