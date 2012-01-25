from django.conf.urls.defaults import patterns, include, url
from mapstream2.stream import views
from mapstream2.listener import views as l_api

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mapstream2.views.home', name='home'),
    url(r'^$', views.home, name='home'),
    url(r'^report$', views.report_event, name='report'),
    
    # data api:
    url(r'^data/(\w+)/(\w*)', views.list_data, name='data_api'),
    #secure api: Only allows access to preconfigured views
    # url(r'^data/(\w+)', views.secure_list_data, name='secure_data_api'),

    # listener api:
    url(r'^listener/(\w+)/(\w*)', l_api.list_data, name='listener_api'),	# will make it more strict eventually -- dont remember what this is for!!
    # url(r'^mapstream2/', include('mapstream2.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
