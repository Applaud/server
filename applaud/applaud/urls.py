from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'applaud.views.home', name='home'),
    # url(r'^applaud/', include('applaud.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


    ####################################################################

    #GET w/ lat and long
    #google places API call
    #close businesses
    #return json to client
#    url(r'^checkin/',)
    
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


    url(r'^/','views.home' )

)
