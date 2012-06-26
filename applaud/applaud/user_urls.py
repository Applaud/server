from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.contrib import admin
import views
import settings

import user_views

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^welcome/', direct_to_template, {'template':'user.html'}),
                       url(r'^$', direct_to_template, {'template':'user.html'}),
                       url(r'^edit_user_profile/',
                           user_views.edit_user_profile,
                           name="edit_user_profile"),

                       )
