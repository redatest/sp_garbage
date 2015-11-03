
# -*- coding: utf-8 -*-
from django.conf.urls import *
from profile.forms import ExRegistrationForm
from registration.backends.default.views import RegistrationView
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin

from offre.sitemap import OfferSitemap, SiteSitemap

import debug_toolbar

sitemaps = {
    'offer' : OfferSitemap,
    'site' : SiteSitemap(['contact', 'news', 'deposer_offre', 'search' ])
}

admin.autodiscover()

urlpatterns = patterns('',

    # main application
    url('^$', "car_shop.views.home", name='home'),

    url('legales/$', "car_shop.views.legales", name='legales'),

    url('utilisation/$', "car_shop.views.utilisation", name='utilisation'),

    url('conditions/$', "car_shop.views.conditions", name='conditions'),
    
    # url('^', include("car_shop.urls")),

    # payment application
    (r'pay/', include('main.urls')),

    url('charge/candidate/(?P<num>\w+)/$', "profile.views.charge", name='charge'),

    (r'^admin/', include(admin.site.urls)),

    url(r"^payments/", include("payments.urls")),

    # offres
    url('^deposer_offre$', "offre.views.deposer_offre", name='deposer_offre'),

    url('^offer/(?P<num>\w+)/$', "offre.views.offer", name='offer'),

    url('^offer/(?P<num>\w+)/edit/$', "offre.views.offer_edit", name='offer_edit'),

    url('^offer/(?P<num>\w+)/disable/$', "offre.views.offer_disable", name='offer_disable'),

    url('^offer/(?P<num>\w+)/activate/$', "offre.views.offer_activate", name='offer_activate'),

    url('^offer/(?P<num>\w+)/postulate/$', "offre.views.offer_postulate", name='offer_postulate'),

    url('^offer/(?P<num>\w+)/mark/$', "offre.views.offer_mark", name='offer_mark'),

    url('^offer/(?P<num>\w+)/(?P<comp>\w+)/unmark/$', "offre.views.offer_unmark", name='offer_unmark'),

    # application
    url('^applications/$', "offre.views.applications", name='applications'),

    url('^application/(?P<offer_id>\w+)/confirm/(?P<user_id>\w+)/set/(?P<app_id>\w+)$', "offre.views.app_confirm", name='app_confirm'),

    url('^application/(?P<offer_id>\w+)/reject/(?P<user_id>\w+)/set/(?P<app_id>\w+)/$', "offre.views.app_reject", name='app_reject'),    

    # alerts
    url('^alert/confirm/(?P<user_id>\w+)/set/(?P<app_id>\w+)$', "profile.views.alert_confirm", name='alert_confirm'),

    url('^alert/reject/(?P<user_id>\w+)/set/(?P<app_id>\w+)/$', "profile.views.alert_reject", name='alert_reject'),    

    # article
    url('^news$', "article.views.news", name='news'),

    url('^news_item/(?P<num>\w+)/$', "article.views.news_item", name='news_item'),

    url('^contact$', "car_shop.views.contact", name='contact'),

    # searching
    url('^search$', "search.views.search", name='search'),

    url(r'^search/$', "search.views.search", name='search'),

    url(r'^search_emp/$', "search.views.search_emp", name='search_emp'),

    url(r'^map_search/$', "search.views.map_search", name='map_search'),

    url(r'^map_search_emp/$', "search.views.map_search_emp", name='map_search_emp'),

    url(r'^search_candidates/$', "search.views.search_candidates", name='search_candidates'),

    url(r'^search_auto/$', "search.views.search_auto", name='search_auto'),

    url(r'^text_search_emp/$', "search.views.text_search_emp", name='text_search_emp'),

    url(r'^text_search/$', "search.views.text_search", name='text_search'),    

    # Profile
    url(r'^profile_login/$', "profile.views.profile_login", name='profile_login'),

    url(r'^candid_profile/$', "profile.views.candid_profile", name='candid_profile'),

    url(r'^candid_profile_edit/(?P<id>\w+)/$', "profile.views.candid_profile_edit", name='candid_profile_edit'),
    
    url(r'^send_alert/(?P<id>\w+)/$', "profile.views.send_alert", name='send_alert'),

    url(r'^emp_profile/$', "profile.views.emp_profile", name='emp_profile'),

    url(r'^company/(?P<num>\w+)/$', "profile.views.company", name='company'),

    url(r'^emp_profile_offres/$', "profile.views.emp_profile_offres", name='emp_profile_offres'),

    url(r'^emp_profile_alerts/$', "profile.views.emp_profile_alerts", name='emp_profile_alerts'),

    url(r'^emp_profile_edit/(?P<id>\w+)/$', "profile.views.emp_profile_edit", name='emp_profile_edit'),

    url(r'^emp_profile_offer_applyers/(?P<id>\w+)/$', "profile.views.emp_profile_offer_applyers", name='emp_profile_offer_applyers'),

    url(r'^candid_profile_marks/$', "profile.views.candid_profile_marks", name='candid_profile_marks'),

    url(r'^candid_profile_alerts/$', "profile.views.candid_profile_alerts", name='candid_profile_alerts'),

    url(r'^candid_profile_application_status/$', "profile.views.candid_profile_application_status", name='candid_profile_application_status'),

    url(r'^candidate/(?P<num>\w+)/$', "profile.views.candidate", name='candidate'),

    url(r'^delete_emp_page/$', "profile.views.delete_emp_page", name='delete_emp_page'),

    url(r'^delete_candid_page/$', "profile.views.delete_candid_page", name='delete_candid_page'),

    url(r'^delete_profile_emp/$', "profile.views.delete_profile_emp", name='delete_profile_emp'),

    url(r'^delete_profile_candid/$', "profile.views.delete_profile_candid", name='delete_profile_candid'),

    # custom registration
    url(r'accounts/register/$', RegistrationView.as_view(form_class = ExRegistrationForm), name = 'registration_register'),

    url(r'accounts/login/$', 'registration.views.login', name = 'authentication_login'),

    (r'^accounts/', include('registration.backends.default.urls')),

    # debug toolbar
    url(r'^__debug__/', include(debug_toolbar.urls)),

    # sitemap
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap' , {'sitemaps': sitemaps} ),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'%s/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'),
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )