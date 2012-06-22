from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template, redirect_to
from django.http import HttpResponseRedirect
from django.contrib import admin
import views
import settings
from registration import views as business_views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^welcome/', direct_to_template, {'template':'employee_welcome.html'}),
                       url(r'^stats/', views.employee_stats,
                           name='employee_stats'),
                       url(r'^$', redirect_to, {'url':'stats'},
                           name='employee_home'),
                       )
