from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template, redirect_to
from django.http import HttpResponseRedirect
from django.contrib import admin
import business_views as views
import settings

admin.autodiscover()

urlpatterns = patterns('',
                       # First time visiting the site
                       url(r'^welcome/', views.business_welcome),
                       
                       # Employee stuff

                       url(r'^business_manage_employees/',
                           # direct_to_template,
                           # {'template':'manage_employees.html'},
                           views.manage_employees,
                           name='business_manage_employees'),
                       
                       url(r'^business_manage_survey/',
                           direct_to_template,
                           {'template':'fail.html'},
                           name='business_manage_survey'),

                       url(r'^business_manage_ratingprofiles',
                           views.manage_ratingprofiles,
                           name="business_manage_ratingprofile"),

                       url(r'^edit_employee/', views.edit_employee),
                       url(r'^delete_employee/', views.delete_employee),
                       url(r'^new_employee/',
                           views.add_employee,
                           name="business_new_employee"),

                       # TODO: employee stats.
                       # url(r'^employee_stats/', views.employee_stats),
                       url(r'^ratingprofiles/',views.list_rating_profiles),                       
                       # Business home
                       url(r'^$',
                           redirect_to,
                           {'url':'analytics'},
                           name="business_home"),
                       
                       # Survey stuff
                       url(r'^survey_create/',views.create_survey),
                       url(r'^get_survey/',views.get_survey),
                       #url(r'^general_feedback/',views.feedback),

                       url(r'^create_rating_profile/',views.create_rating_profile),
                          
                       # Everything related to newsfeed
                       url(r'^business_manage_newsfeed/',
                           views.manage_newsfeed,
                           name="business_manage_newsfeed"),
                       url(r'^newsfeed_create/',views.newsfeed_create),
                       url(r'^edit_newsfeed/', views.edit_newsfeed),
                       url(r'^delete_newsfeed_item/', views.delete_newsfeed_item),
                       
                       # Checking analytics.
                       url(r'^analytics/', views.analytics, name="analytics"),
                       )
