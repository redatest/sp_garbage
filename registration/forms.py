# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import UNUSABLE_PASSWORD, is_password_usable, get_hasher
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site


class RegistrationForm(forms.Form):
    required_css_class = 'required'
    username = forms.RegexField(regex=r'^[\w\s.@+-]+$',
                                max_length=40,
                                label=_("Nom d\'utilisateur"),
                                error_messages={'invalid': _("Le nom d\'utilisateur ne peut avoir que des lettres, Chiffres et les characteres @/./+/-/_ .")})
    email = forms.EmailField(label=_("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Mot de passe"))
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Verifier le mot de passe"))

    def clean_username(self):
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("Le nom d\'utilisateur %s est deja pris"%self.cleaned_data["username"]))
        else:
            return self.cleaned_data['username']

    def clean_password1(self):
        password = self.cleaned_data['password1']
        length = len(password)
        if length < 8: raise forms.ValidationError("Il faut taper au moin 8 lettres.")
        return password

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("Les deux mot de passe ne sont pas identiques"))
        return self.cleaned_data



class RegistrationFormTermsOfService(RegistrationForm):
    tos = forms.BooleanField(widget=forms.CheckboxInput,
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})

class RegistrationFormUniqueEmail(RegistrationForm):
    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']

class RegistrationFormNoFreeEmail(RegistrationForm):
    bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com', 'googlemail.com', 'hotmail.com', 'hushmail.com',
                   'msn.com', 'mail.ru', 'mailinator.com', 'live.com', 'yahoo.com']

    def clean_email(self):
        email_domain = self.cleaned_data['email'].split('@')[1]
        if email_domain in self.bad_domains:
            raise forms.ValidationError(_("Registration using free email addresses is prohibited. Please supply a different email address."))
        return self.cleaned_data['email']


class AuthenticationForm(forms.Form):

    username = forms.CharField(label=_("Nom d'utilisateur"), max_length=40)
    password = forms.CharField(label=_("Mot de passe"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Corrigez votre nom SVP. "
                           "Il faut savoir que les deux champs sont sensibles a la casse."),
        'no_cookies': _("Il faut activer les Cookies sur votre navigateur "
                        "qui sont nécéssaires pour l'authentification."),
        'inactive': _("Ce compte est inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):

        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'])
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(self.error_messages['no_cookies'])

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
