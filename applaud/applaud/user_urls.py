from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.contrib import admin
import views
import settings
from registration import views as business_views
import user_views as views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^welcome/', direct_to_template, {'template':'user.html'}),
                       url(r'^$', direct_to_template, {'template':'user.html'}),
                       url(r'^edit_user_profile/',
                           views.edit_user_profile,
                           name="edit_user_profile"),

                       )
