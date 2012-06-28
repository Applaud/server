from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template, redirect_to
import user_views as views

urlpatterns = patterns('',
                       url(r'^welcome/$',
                           redirect_to,
                           {'url':'/user/edit_user_profile/'},
                           name="user_welcome"),

                       url(r'^$', direct_to_template, {'template':'user.html'},
                           name="user_home"),

                       url(r'^edit_user_profile/$',
                           views.edit_user_profile,
                           name="edit_user_profile"),
                       )
