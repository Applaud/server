from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
import views
import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'applaud.views.home', name='home'),
    # url(r'^applaud/', include('applaud.foo.urls')),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


    ####################################################################

    #GET w/ lat and long
    #google places API call
    #close businesses
    #return json to client
    url(r'^checkin/',views.checkin),
    url(r'^newsfeed_create/',views.newsfeed_create),
    url(r'^newsfeed/',views.nfdata),                       
    url(r'^new_employee/',views.create_employee),
    url(r'^employees/',views.employee_list),
    url(r'^create_rating_profile/',views.create_rating_profile),
    url(r'^ratingprofiles/',views.list_rating_profiles),
    url(r'^survey_create/',views.create_survey),

    #GET w/ GID
    #validate GID
    #get or creat business - (create default form)
    #get for fields
    #return json of fields to client
#    url(r'^place/',)

    #POST fields & values
    #stores value in database
    #return success message
    #if error saving, or with data validation
    #return error message
#    url(r'^submit/',)


    url(r'^/',views.home),
    url(r'^example/$',views.example),
    url(r'^example2/$',views.example2),
    url(r'^example3/$',views.example3),
)
