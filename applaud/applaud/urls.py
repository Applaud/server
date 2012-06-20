from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import views
import settings
from registration import views as business_views

urlpatterns = patterns('',


                       # What to do with static files. Always served from /static
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT}),

                       # Home, sweet home
                       url(r'^$', views.index),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),

                       # IOS notifies us of where device is. We return business locations
                       url(r'^whereami/',views.whereami),

                       # Creating/editing newsfeed, looking at the newsfeed
                       url(r'^newsfeed_create/',views.newsfeed_create),
                       url(r'^newsfeed/',views.nfdata),
                       url(r'^edit_newsfeed/', views.edit_newsfeed),
                       url(r'^delete_newsfeed_item/', views.delete_newsfeed_item),
                       
                       # Creating/editing/viewing employees
                       url(r'^new_employee/',views.create_employee),
                       url(r'^create_rating_profile/',views.create_rating_profile),
                       url(r'^ratingprofiles/',views.list_rating_profiles),
                       url(r'^edit_employee/', views.edit_employee),
                       url(r'^delete_employee/', views.delete_employee),

                       # Getting and posting employee data from iOS
                       url(r'^evaluate/', views.evaluate),
                       url(r'^employees/',views.employee_list),
                       
                       # Creating/editing/viewing surveys
                       url(r'^survey_create/',views.create_survey),
                       url(r'^get_survey/',views.get_survey),
                       
                       # Posting survey response
                       url(r'^survey_respond/', views.survey_respond),
                       
                       # Registering end-users. Allowing them to configure their account online
                       (r'^accounts/', include('registration.backends.default.urls')),

                       # Static JSON data that can be used for testing when the internet's down
                       url(r'^example/$',views.example),
                       url(r'^example2/$',views.example2),
                       url(r'^example3/$',views.example3),
                       
                       # General feedback.
                       url(r'^general_feedback/$', views.general_feedback),

                       # Getting the CSRF token for mobile devices
                       url(r'^csrf/$', views.get_csrf),
                       )

