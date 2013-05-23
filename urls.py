from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^patient/$', 'patient.views.search', name='patient_search'),
    url(r'^patient/add/$', 'patient.views.add', name='patient_add'),
    url(r'^patient/(?P<patient_id>\d+)/$', 'patient.views.edit', name='patient_edit'),
# Examples:
# url(r'^$', 'geneticist.views.home', name='home'),
# url(r'^geneticist/', include('geneticist.foo.urls')),

# Uncomment the admin/doc line below to enable admin documentation:
# url(r'^admin/doc/',
# include('django.contrib.admindocs.urls')),

# Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
