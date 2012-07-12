from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib import messages
from PIL import Image as PImage
import registration.forms as registration_forms
import os
import json
import settings
import sys
from applaud.models import EmployeeProfile
import views
from django.core.files import File

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
    return render_to_response('employee_stats.html', {}, context_instance=RequestContext(request))


@employee_view
def get_stats(request):
    '''Gives statistics for a particular employee (given in request). This
    is accessed through the apatapa website when an employee is logged in.
    '''
    profile = request.user
    employee = profile.employeeprofile
    rating_profile = employee.rating_profile

    if request.method == 'GET':
        return_data={}

        all_ratings = sorted(list(employee.rating_set.all()),key=lambda e:e.date_created)
        encoded_employee = views.EmployeeEncoder().default(employee)
        encoded_employee['ratings'] = [views.RatingEncoder().default(r) for r in all_ratings]
    
        return_data['employees']=[encoded_employee]
    
        return HttpResponse(json.dumps({'data':return_data}),
                            mimetype='application/json')

    return render_to_response('employee_stats.html', {}, context_instance=RequestContext(request))

@employee_view
def list_employee(request):
    """This method is borrowed heavily from the list_employee method in business_view
    """
    if request.method == 'GET':
        employee = request.user.employeeprofile
        return HttpResponse(json.dumps({'employee':employee},
                                       cls=views.EmployeeEncoder),
                            mimetype='application/json')       
    else:
        return HttpResponse({'foo':"FOOO!"})

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
                    image = PImage.open(request.FILES['profile_picture'])
                except IOError:
                    # For now, we'll just ignore bad images.
                    messages.add_message(request, messages.ERROR, "Something went wrong uploading the image.")
                    return HttpResponseRedirect(reverse('employee_analytics'))
                if not image.format in ['PNG', 'JPEG', 'BMP']:
                    messages.add_message(request, messages.ERROR, "Invalid image type. Please submit a PNG, JPG, or BMP.")
                    return HttpResponseRedirect(reverse('employee_analytics'))
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

                profile.profile_picture = imagepath
                profile.save()

        messages.add_message(request, messages.SUCCESS, "Profile saved successfully!")

        return HttpResponseRedirect(reverse("employee_analytics"))
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


