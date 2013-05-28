from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^patient/$', 'patient.views.search', name='patient_search'),
    url(r'^patient/add/$', 'patient.views.add', name='patient_add'),
    url(r'^patient/(?P<patient_id>\d+)/$', 'patient.views.edit', name='patient_edit'),
    url(r'^admin/', include(admin.site.urls)),
)



if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media\/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),)

    urlpatterns += staticfiles_urlpatterns()
