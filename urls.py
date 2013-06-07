from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin


admin.autodiscover()


js_info_dict = {'domain': 'djangojs', 'packages': ('django.conf', 'django.contrib.admin',), }


urlpatterns = patterns('',
    url(r'^patient/$', 'patient.views.search', name='patient_search'),
    url(r'^patient/add/$', 'patient.views.add', name='patient_add'),
    url(r'^patient/(?P<patient_id>\d+)/$', 'patient.views.edit', name='patient_edit'),
    url(r'^mkb\.json$', 'mkb.views.mkb', name='mkb'),
    url(r'^kladr.json$', 'kladr.views.kladr', name='kladr'),
    (r'^admin/jsi18n/', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^admin/', include(admin.site.urls)),
)



if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media\/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),)

    urlpatterns += staticfiles_urlpatterns()
