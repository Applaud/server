from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import views
import settings
from registration import views as business_views

admin.autodiscover()

urlpatterns = patterns('',
                       # What to do with static files. Always served from /static
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT}),

                       url(r'^$', views.index),
                       (r'^business/', include(business_urls.py)),
                       (r'^mobile/', include(mobile_urls.py)),
                       (r'^employee/', include(employee_urls.py)),
                       (r'^user/', include(user_urls.py)),
                       (r'^accounts/', include('registration.backends.default.urls')),

                       )

