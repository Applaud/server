from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.template import RequestContext
import registration.forms as registration_forms
import json
import settings

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

        # Return string for rendering in google charts
        return render_to_response('employee_stats.html',
                                  {'chartdata':json.dumps( success_chart ),
                                   'employee':employee})

    return HttpResponseForbidden("employee not logged in")

@csrf_protect
def edit_profile(request):
    if request.user.is_authenticated() and 'employeeprofile' in dir(request.user):
        if request.method == 'POST':
            form = registration_forms.EmployeeProfileForm(request.POST, request.FILES)
            if form.is_valid():
                profile = request.user.employeeprofile
                # Set the image name based upon employeeprofile id and business id
                # imagename = businessname.businessid/employeefn_employeeln.employeeid.fileext
                fileext = request.FILES['profile_picture'].name.split('.')[-1]
                imagename = "%s.%d/%s_%s.%d.%s"%(profile.business.user.username.replace(" ","_"),
                                                 profile.business.id,
                                                 profile.user.first_name,
                                                 profile.user.last_name,
                                                 profile.id,
                                                 fileext)
                with open( settings.MEDIA_ROOT+imagename, "wb+" ) as destination:
                    for chunk in request.FILES['profile_picture']:
                        destination.write(chunk)
                destination.close()
                return render_to_response('employee_stats.html',
                                          {'message':"Your profile has been saved successfully."},
                                          context_instance=RequestContext(request))
        else:
            form = registration_forms.EmployeeProfileForm()
        return render_to_response('employee_profile.html',
                                  {'form':form},
                                  context_instance=RequestContext(request))