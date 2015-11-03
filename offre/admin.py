# -*- coding: utf-8 -*-
from django.contrib import admin
from offre.models import Offer

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe


# add image display to car administration
class AdminImageWidget(AdminFileWidget):
	def render(self, name, value, attrs=None):
		output = []
		if value and getattr(value, "url", None):
			image_url = value.url
			file_name=str(value)
			output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" width="80" height="80" /></a> <br/> %s ' % \
				(image_url, image_url, file_name, _('Change:')))
		output.append(super(AdminFileWidget, self).render(name, value, attrs))
		return mark_safe(u''.join(output))

class OfferAdmin(admin.ModelAdmin):
	list_display 	= ('title', 'slug', 'offerType', 'region', 'offerType', 'salary', 'user')
	readonly_fields = ('slug',)
	# delete selected car and it's  file

	fieldsets = (
	( 'Infos générales:',       {'fields': [ 'title', 'slug', 'views', 'created', 'modified', 'expired', 'description' ] }),
    ( 'Secteur de l\'offre:',   {'fields':  [ ( 'region' )],        			  'classes': ['extrapretty'] }),
    ( 'Type de l\'offre:',      {'fields': [ ( 'offerType', 'immediate' ) ],      'classes': ['extrapretty'] }),
    ( 'Salaire proposé:',       {'fields': [ 'salary' ],						  'classes': ['extrapretty'] }),
    ( 'Activer / désactiver:',  {'fields': [ ('activated') ],  					  'classes': ['extrapretty'] }),
    ( 'Recuteur associé:',      {'fields': [ ('user') ],   						  'classes': ['extrapretty'] }),

    )
	
admin.site.register(Offer, OfferAdmin)
