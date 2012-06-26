from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.template import RequestContext
from PIL import Image as PImage
import registration.forms as registration_forms
import os
import json
import settings
import sys
from applaud.models import EmployeeProfile

def employee_stats(request):
    '''Gives statistics for a particular employee (given in request). This
    is accessed through the apatapa website when an employee is logged in.
    '''
    if request.user.is_authenticated():
        profile = ""
        employee = ""
	try:
            employee = request.user
	    profile = employee.employeeprofile
	except EmployeeProfile.DoesNotExist:
	    return HttpResponseNotFound("Could not find the requested page.")
        rating_profile = profile.rating_profile
        if not rating_profile:
            # Employer hasn't created a ratingprofile
            return HttpResponseRedirect("/")
        ratings = profile.rating_set

        # List of valid dimensions for rating
        dimensions = rating_profile.dimensions

        success_chart = []
        axis = ['dimension', 'poor', 'fair', 'good', 'excellent', 'glorious']
        success_chart.append(axis)
        for i in range(len(dimensions)):
            row = [ dimensions[i] ]
            rating_vals = []
            for j in range(5):
                rating_vals.append(len(ratings.filter(title=dimensions[i],
                                                      rating_value=j+1)))
            row.extend(rating_vals)
            success_chart.append(row)

        imagepath = "%s.%d"%(profile.business.user.username.replace(" ","_"),
                             profile.business.id)

        imagename = "%s_%s.%d.%s"%(employee.first_name,
                                   employee.last_name,
                                   profile.id,
                                   profile.profile_picture.name.split('.')[-1])

        sys.stderr.write(imagepath)
        sys.stderr.write(imagename)

        # Return string for rendering in google charts
        return render_to_response('employee_stats.html',
                                  {'chartdata':json.dumps( success_chart ),
                                   'employee':employee,
                                   'image':"%s/%s"%(imagepath,imagename)},
                                  context_instance=RequestContext(request))

    return HttpResponseForbidden("employee not logged in")

@csrf_protect
def edit_profile(request):
    if request.user.is_authenticated():
        try:
            profile = request.user.employeeprofile
        except:
            return HttpResponseRedirect('/')
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
                destination.close()

                # Generate a thumbnail
                thumb = PImage.open( imagepath )
                thumb.thumbnail((128,128), PImage.ANTIALIAS)
                thumb.save( "%s/thumb_%s"%(imagedir,imagename) )
                
                return HttpResponseRedirect('/employee/profilesuccess/')
        else:
            form = registration_forms.EmployeeProfileForm(instance=profile)
        return render_to_response('employee_profile.html',
                                  {'form':form},
                                  context_instance=RequestContext(request))

def welcome(request):
    '''Welcomes an employee the first time that they log in
    '''
    if request.user.is_authenticated():
        profile = ""
        employee = ""
	try:
            employee = request.user
	    profile = employee.employeeprofile
	except EmployeeProfile.DoesNotExist:
	    return HttpResponseNotFound("Could not find the requested page.")
        
        return render_to_response("employee_welcome.html",
                                  {"employee":profile})
                               
