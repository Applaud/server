from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.contrib import admin
import views
import settings
from registration import views as business_views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^welcome/', direct_to_template, {'template':'employee_welcome.html'}),
                       #url(r'^/$', direct_to_template, {'template':'employee.html'}),
                       )
