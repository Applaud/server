from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.contrib import admin
import views
import settings
from registration import views as business_views

admin.autodiscover()

urlpatterns = patterns('',
                       # IOS notifies us of where device is. We return business locations
                       url(r'^whereami/',views.whereami),
                       url(r'^checkin/$',views.checkin),

                       # Getting and posting employee data from iOS
                       url(r'^evaluate/', views.evaluate),
                       url(r'^employees/',views.employee_list),
                       
                       # Posting survey response
                       url(r'^survey_respond/', views.survey_respond),

                       # Static JSON data that can be used for testing when the internet's down
                       url(r'^example/$',views.example),
                       url(r'^example2/$',views.example2),
                       url(r'^example3/$',views.example3),
                       
                       # General feedback.
                       url(r'^general_feedback/$', views.general_feedback),

                       # Getting the CSRF token for mobile devices
                       url(r'^csrf/$', views.get_csrf),
                       )                      
