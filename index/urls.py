from django.conf.urls import patterns, url
from views import (
        IndexView, QuestView, LoginView, SignUpView,
        ErrorView,
        )

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     #url(r'^/', 'index.home', name='home'),
     url(r'^$', IndexView.as_view()), 
     url(r'^quest/(?P<uid>\w+)/$', QuestView.as_view(), name="single_quest"),
     url(r'^mark/failed/$', 'mark_failed', name="mark_failed"),
     url(r'^mark/clear/$', 'mark_day_cleared', name="mark_day_cleared"),
     url(r'^signup/$', SignUpView.as_view(), name="signup"),
     url(r'^login/$', LoginView.as_view(), name="login"),
     url(r'^logout/$', 'index.views.user_logout', name="logout"),
     url(r'^errors/$', ErrorView.as_view(), name="errors"),

     url(r'^record/error$', 'index.views.mark_failed', name="mark_failed"),
     url(r'^logout/$', 'index.views.user_logout', name="logout"),
     url(r'^update/$', 'index.views.update_quests', name="update_quests"),
     url(r'^update/single/$', 'index.views.get_single_quest', name="update_single_quest"),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
