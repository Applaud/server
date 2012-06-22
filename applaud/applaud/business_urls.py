from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.contrib import admin
import business_views as views
import settings

admin.autodiscover()

urlpatterns = patterns('',
                       # First time visiting the site
                       url(r'^welcome/', views.business_welcome),
                       
                       # Employee stuff
                       url(r'^edit_employee/', views.edit_employee),
                       url(r'^delete_employee/', views.delete_employee),

                       # TODO: employee stats.
                       # url(r'^employee_stats/', views.employee_stats),
                       url(r'^ratingprofiles/',views.list_rating_profiles),                       
                       # Business home
                       url(r'^$', direct_to_template, {'template':'business.html'}),
                       
                       # Survey stuff
                       url(r'^survey_create/',views.create_survey),
                       url(r'^get_survey/',views.get_survey),
                       #url(r'^general_feedback/',views.feedback),

                       url(r'^create_rating_profile/',views.create_rating_profile),
                          
                       # Creating/editing newsfeed, looking at the newsfeed
                       url(r'^newsfeed_create/',views.newsfeed_create),
                       url(r'^newsfeed/',views.nfdata),
                       url(r'^edit_newsfeed/', views.edit_newsfeed),
                       url(r'^delete_newsfeed_item/', views.delete_newsfeed_item),

                       )


