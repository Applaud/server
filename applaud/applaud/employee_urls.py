from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template, redirect_to
from django.http import HttpResponseRedirect
from django.contrib import admin
import views
import employee_views
import settings

urlpatterns = patterns('',
                       url(r'^stats/',
                           employee_views.employee_stats,
                           name='employee_stats'),
                       url(r'^welcome/',redirect_to, {'url':'profile'}),
                       url(r'^$', redirect_to, {'url':'stats'},
                           name='employee_home'),
                       url(r'^profile/',
                           employee_views.edit_profile,
                           name='employee_profile'),
                       url(r'^profilesuccess/',
                           direct_to_template,
                           {'template':'profile_success.html'}),
        )
