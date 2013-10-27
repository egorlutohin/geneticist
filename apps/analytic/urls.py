#coding: utf8
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import views


urlpatterns = patterns('',
    url(r'^life/$', views.life, name='analytic_life'),
)
