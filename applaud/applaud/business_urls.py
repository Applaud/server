from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template, redirect_to
import business_views as views

urlpatterns = patterns('',
                       # First time visiting the site
                       url(r'^welcome/$', views.business_welcome),
                       
                       # Employee stuff
                       url(r'^manage_employees/$',
                           # direct_to_template,
                           # {'template':'manage_employees.html'},
                           views.manage_employees,
                           name='business_manage_employees'),
                       url(r'^delete_employee/$',
                           views.delete_employee,
                           name='business_delete_employee'),
                       url(r'^new_employee/$',
                           views.add_employee,
                           name="business_new_employee"),
                       
                       # Survey stuff
                       url(r'^manage_survey/$', views.manage_survey,
                           name="business_manage_survey"),

                       # Rating Profiles
                       url(r'^manage_ratingprofiles/$',
                           views.manage_ratingprofiles,
                           name="business_manage_ratingprofiles"),
                       url(r'^new_ratingprofile/$',
                           views.new_ratingprofile,
                           name="business_new_ratingprofile"),
                       url(r'^list_ratingprofiles/$',
                           views.list_rating_profiles,
                           name="business_list_ratingprofiles"),
  
                       # Business home
                       url(r'^$',
                           redirect_to,
                           {'url':'analytics'},
                           name="business_home"),
                       


                          
                       # Everything related to newsfeed
                       url(r'^manage_newsfeed/$',
                           views.manage_newsfeed,
                           name="business_manage_newsfeed"),
                       url(r'^newsfeed_list/$',
                           views.newsfeed_list,
                           name='business_newsfeed_list'),
                       
                       # Checking analytics.
                       url(r'^analytics/$', views.analytics, name="analytics"),
                       )
