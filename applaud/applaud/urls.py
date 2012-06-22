from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import views
import settings
from registration import views as business_views
import business_urls, mobile_urls, employee_urls, user_urls

# Import other urlconfs
import business_urls
import mobile_urls
import employee_urls
import user_urls

admin.autodiscover()

urlpatterns = patterns('',
                       # What to do with static files. Always served from /static
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT}),
                       url(r'^$', views.index),
                       (r'^business/', include(business_urls)),
                       (r'^mobile/', include(mobile_urls)),
                       (r'^employee/', include(employee_urls)),
                       (r'^user/', include(user_urls)),
                       (r'^accounts/', include('registration.backends.default.urls')),
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
