from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template, redirect_to
from django.http import HttpResponseRedirect
from django.contrib import admin
import views
import business_views
import settings

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^welcome/', direct_to_template, {'template':'employee_welcome.html'}),
                       # TODO: employee stats
                       # url(r'^stats/', business_views.employee_stats,
                       #    name='employee_stats'),
                       url(r'^$', redirect_to, {'url':'stats'},
                           name='employee_home'),
                       )
