from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template, redirect_to
from django.http import HttpResponseRedirect
from django.contrib import admin
import views
import employee_views
import settings

urlpatterns = patterns('',
                       # Stats page.
                       url(r'^stats/$',
                           employee_views.employee_stats,
                           name="employee_analytics"),

                       url(r'^get_stats/$',
                           employee_views.get_stats,
                           name='employee_stats'),

                       url(r'^list_employee/$',
                           employee_views.list_employee,
                           name='employee_list_employee'),

                       # Welcome page. We visit this right after registering.
                       url(r'^welcome/$',
                           redirect_to,
                           {'url':'/employee/profile/'},
                           name="employee_welcome"),

                       # Landing page
                       url(r'^$', redirect_to, {'url':'stats'},
                           name='employee_home'),

                       # Profile-editing page
                       url(r'^profile/$',
                           employee_views.edit_profile,
                           name='employee_profile'),

                       # Where we go when editing profile was successful
                       url(r'^profilesuccess/$',
                           direct_to_template,
                           {'template':'profile_success.html'},
                           name="employee_profile_success"),


        )
