from django.conf.urls.defaults import patterns, include, url

import views

event_patterns = patterns('', 
                          url(r'^$', views.time, name='time'),
                          url(r'^(?P<year>\d{4})$', views.time, name='time_year'),
                          url(r'^(?P<year>\d{4})/(?P<month>\d{2})$', views.time, name='time_year_month'),
                          url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<week>\d{2})$', views.time, name='time_year_month_week'),
                          )

group_patterns = patterns('', 
                          url(r'^$', views.group, name='group_default'),
                          url(r'^(?P<mode>\w+)$', views.group, name='group'),
                          url(r'^(?P<mode>\w+)/(?P<year>\d{4})$', views.group, name='group_year'),
                          url(r'^(?P<mode>\w+)/(?P<year>\d{4})/(?P<month>\d{2})$', views.group, name='group_year_month'),
                          url(r'^(?P<mode>\w+)(?P<year>\d{4})/(?P<month>\d{2})/(?P<week>\d{2})$', views.group, name='group_year_month_week'),
                          )

urlpatterns = patterns('',
                       url(r'^events/', include(event_patterns)),
                       url(r'^group/', include(group_patterns)),
)
