from django.conf.urls import patterns, include, url
from views import (
        IndexView, QuestView
        )

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     #url(r'^/', 'index.home', name='home'),
     url(r'^$', IndexView.as_view()), 
     url(r'quest/(?P<uid>\w+)/$', QuestView.as_view(), name="single_quest"),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
