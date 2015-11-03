# -*- coding: utf-8 -*-
from django import forms
from car_shop.model_choices import *
from article.widgets import TinyMCEWidget
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
import datetime


class ArticleAdminForm(forms.ModelForm):
	body=forms.CharField(widget=TinyMCEWidget())

	class Meta:
		model = get_model('article', 'Article')

