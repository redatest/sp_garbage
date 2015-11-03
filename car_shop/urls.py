from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
 	url('/$', "car_shop.views.home", name='home'),
)
