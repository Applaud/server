from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.contrib import admin
import mobile_views as views
import settings

admin.autodiscover()

urlpatterns = patterns('',
                       # IOS notifies us of where device is. We return business locations
                       url(r'^whereami/$',views.whereami),
                       url(r'^checkin/$',views.checkin),

                       # Getting and posting Polls data
                       url(r'^get_polls/$', views.get_polls),
                       url(r'^submit_poll/$', views.submit_poll),
                       url(r'^create_poll/$', views.create_poll),
                       url(r'^rate_poll/$', views.rate_poll),

                       # Getting and posting Threads and ThreadPosts
                       url(r'^get_threads/$', views.get_threads),
                       url(r'^create_thread/$', views.create_thread),
                       url(r'^rate_thread/$', views.rate_thread),
                       url(r'^submit_post/$', views.submit_post),
                       url(r'^rate_post/$', views.rate_post),

                       # Getting and posting employee data from iOS
                       url(r'^evaluate/$', views.evaluate),
                       url(r'^employees/$',views.employee_list),
                       
                       # Posting survey response
                       url(r'^get_survey/$', views.get_survey),
                       url(r'^survey_respond/$', views.survey_respond),

                       # Static JSON data that can be used for testing when the internet's down
                       url(r'^example/$',views.example),
                       url(r'^example2/$',views.example2),
                       url(r'^example3/$',views.example3),
                       
                       # General feedback.
                       url(r'^general_feedback/$', views.general_feedback),
                       
                       # Photos.
                       url(r'^post_photo/$', views.post_photo),
                       url(r'^get_photos/$', views.get_photos),
                       url(r'^comment_photo/$', views.comment_photo),
                       url(r'^get_photo_comments/$', views.photo_comments),
                       
                       # Getting the CSRF token for mobile devices
                       url(r'^newsfeed/$',views.nfdata),

                       )                      
