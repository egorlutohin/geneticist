from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin


admin.autodiscover()


js_info_dict = {'domain': 'djangojs', 'packages': ('django.conf', 'django.contrib.admin',), }


urlpatterns = patterns('',
    url(r'^$', 'patient.views.search', name='patient_search'),
    url(r'^add/$', 'patient.views.add', name='patient_add'),
    url(r'^(?P<patient_id>\d+)/$', 'patient.views.edit', name='patient_edit'),
    url(r'^(?P<patient_id>\d+)/history/$', 'patient.views.history', name='patient_history'),
    url(r'^mkb\.json$', 'mkb.views.mkb', name='mkb'),
    url(r'^kladr.json$', 'kladr.views.kladr', name='kladr'),
    (r'^admin/jsi18n/', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^%s$' % settings.LOGIN_URL[1:], 'django.contrib.auth.views.login', name='login'),
    url(r'^%s$' % settings.LOGOUT_URL[1:], 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}, name='logout',),
)



if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media\/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),)

    urlpatterns += staticfiles_urlpatterns()
