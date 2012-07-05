from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from PIL import Image as PImage
import registration.forms as registration_forms
import os
import json
import settings
import sys
from applaud.models import EmployeeProfile
import views

# 'employee_view' decorator.
def employee_view(view):
    '''
    Checks an EmployeeView to make sure that a user is logged in and
    is in fact an employee (i.e., has an EmployeeProfile) before the
    view is executed. If either of these tests fail, the user is redirected
    to the appropriate page.
    '''
    def goto_login(*args, **kw):
        return HttpResponseRedirect(reverse("auth_login"))

    def goto_home(*args, **kw):
        return HttpResponseRedirect(reverse("home"))

    def wrapper(*args, **kw):
        request = args[0]
        if not request.user.is_authenticated():
            return goto_login(*args, **kw)
        try:
            profile = request.user.employeeprofile
        except EmployeeProfile.DoesNotExist:
            return goto_home(*args, **kw)

        return view(*args, **kw)
            
    return wrapper

@employee_view
def employee_stats(request):
    '''Gives statistics for a particular employee (given in request). This
    is accessed through the apatapa website when an employee is logged in.
    '''
    employee = request.user
    profile = employee.employeeprofile
    rating_profile = profile.rating_profile

    # List of valid dimensions for rating
    dimensions = list(rating_profile.rateddimension_set.all())

    return_data = {}
    return_data['dimensions'] = [views.RatedDimensionEncoder().default(dim) for dim in dimensions]
    all_ratings = sorted(list(profile.rating_set.all()),key=lambda e:e.date_created)

    encoded_employee = views.EmployeeEncoder().default(profile)
    encoded_employee['ratings'] = [views.RatingEncoder().default(r) for r in profile.rating_set.all()]
    return_data['employees'] = [encoded_employee]
    
    if request.method == 'GET':
        # Return string for rendering in google charts
        return render_to_response('employee_stats.html',
                                  {'employee':employee,
                                   'image':_profile_picture(profile)},
                                  context_instance=RequestContext(request))

    # Pure JSON, for POST
    return HttpResponse(json.dumps({'data':return_data}),
                        mimetype='application/json')


def _profile_picture(em_profile, thumb=True):
    '''
    Returns the path to the profile picture for the given employee.
    Gives the default profile picture if no specific one exists.

    thumb = True/False (whether or not to return a thumbnail version)
    '''
    employee = em_profile.user

    # See note in edit_profile about this naming scheme
    imagepath = "%s.%d"%(em_profile.business.user.username.replace(" ","_"),
                         em_profile.business.id)

    imagename = "%s_%s.%d.%s"%(employee.first_name,
                               employee.last_name,
                               em_profile.id,
                               em_profile.profile_picture.name.split('.')[-1])
    if thumb:
        imagename = 'thumb_'+imagename

    # Does this file exist?
    image_url = "%s/%s"%(imagepath,imagename)
    if not os.path.exists(settings.MEDIA_ROOT + image_url):
        image_url = settings.DEFAULT_PROFILE_IMAGE

    return image_url

@employee_view
@csrf_protect
def edit_profile(request):
    profile = request.user.employeeprofile
    if request.method == 'POST':
        form = registration_forms.EmployeeProfileForm(request.POST,
                                                      request.FILES,
                                                      instance=profile)
        if form.is_valid():
            form.save()
            # ---------- HANDLE IMAGE UPLOAD ----------
            # Set the image name based upon employeeprofile id and business id
            # imagename = employeefn_employeeln.employeeid.fileext
            # imagedir = MEDIA_ROOT/businessname.businessid
            if 'profile_picture' in request.FILES:
                # First off, make sure it's a actually an image, and that
                # it's a filetype we will accept.
                try:
                    image = Image.open(request.FILES['profile_picture'])
                except IOError:
                    # For now, we'll just ignore bad images.
                    return HttpResponseRedirect(reverse('employee_profile_success'))
                if not image.format in ['PNG', 'JPEG', 'BMP']:
                    return HttpResponseRedirect(reverse('employee_profile_success'))
                fileext = request.FILES['profile_picture'].name.split('.')[-1]
                imagedir = "%s%s.%d"%(settings.MEDIA_ROOT,
                                      profile.business.user.username.replace(" ","_"),
                                      profile.business.id)
                if not os.path.exists(imagedir):
                    os.makedirs(imagedir)
                imagename = "%s_%s.%d.%s"%(profile.user.first_name,
                                           profile.user.last_name,
                                           profile.id,
                                           fileext)
                imagepath = "%s/%s"%(imagedir,imagename) 
                with open( imagepath, "wb+" ) as destination:
                    for chunk in request.FILES['profile_picture']:
                        destination.write(chunk)

                # Generate a thumbnail
                thumb = PImage.open( imagepath )
                thumb.thumbnail((128,128), PImage.ANTIALIAS)
                thumb.save( "%s/thumb_%s"%(imagedir,imagename) )

            return HttpResponseRedirect(reverse("employee_profile_success"))
    else:
        form = registration_forms.EmployeeProfileForm(instance=profile)
    return render_to_response('employee_profile.html',
                              {'form':form,
                               'image':_profile_picture(profile)},
                              context_instance=RequestContext(request))

@employee_view
def welcome(request):
    '''Welcomes an employee the first time that they log in
    '''
    profile = request.user.employeeprofile
    return render_to_response("employee_welcome.html",
                              {"employee":profile})


