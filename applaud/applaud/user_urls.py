from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template, redirect_to
import user_views as views

urlpatterns = patterns('',
                       url(r'^welcome/$',
                           redirect_to,
                           {'url':'/user/edit_user_profile/'},
                           name="user_welcome"),

                       url(r'^$', views.view_previous_responses,
                           name="user_home"),
                       )



                   
