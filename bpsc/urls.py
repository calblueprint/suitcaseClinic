from django.conf.urls import *
from bpsc.views import search, survey, home, contact
from django.views.generic import TemplateView # Test

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bpsc.views.home', name='home'),
    # url(r'^bpsc/', include('bpsc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    (r'^$', home),
    (r'^survey/$', survey),
    (r'^search/$', search),
    (r'^contact/$', contact),
    
)
