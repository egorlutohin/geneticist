#coding: utf8
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import views


urlpatterns = patterns('',
    url(r'^$', views.main, name='analytic'),
    url(r'^life/$', views.life, name='analytic_life'),
    url(r'^nosology/$', views.nosology, name='analytic_nosology'),
    url(r'^new_diagnosis/$', views.new_diagnosis, name='analytic_new_diagnosis'),
    url(r'^visit/$', views.visit, name='analytic_visit'),
)
