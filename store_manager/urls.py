from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'store_manager.views.home', name='home'),
    # url(r'^store_manager/', include('store_manager.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^inventory/', include('inventory_sync.urls')),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
)
