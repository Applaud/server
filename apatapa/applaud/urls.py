from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import views
import settings

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
                       url(r'^$', views.index, name="home"),
                       (r'^business/', include(business_urls)),
                       (r'^mobile/', include(mobile_urls)),
                       (r'^employee/', include(employee_urls)),
                       (r'^user/', include(user_urls)),
                       (r'^overview/', direct_to_template,

                        {'template':'overview.html'}),
                       
                       # Register the email of a beta user
                        (r'^register_beta/', views.register_beta),
                        
                       (r'^about/', direct_to_template,
                        {'template':'about.html'}),

                       # These are to do with messages and inbox.
                       url(r'^messages/', views.view_inbox,
                           name="messages"),
                       url(r'^get_inbox/', views.get_inbox,
                           name="get_inbox"),
                       url(r'^send_message/', views.send_message,
                           name="send_message"),


                       (r'^features/', direct_to_template,
                        {'template':'features.html'}),

                       (r'^accounts/', include('registration.backends.default.urls')),
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



