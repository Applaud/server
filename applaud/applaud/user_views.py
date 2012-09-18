from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import BusinessProfile, EmployeeProfile
from django.template import RequestContext, Template
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.core.urlresolvers import reverse
from datetime import datetime, date
from django.contrib.auth.models import Group, User
import sys
import json
import urllib2
from applaud import forms
from applaud import models
from registration import forms as registration_forms

# 'user_view' decorator.
def user_view(view):
    '''
    Checks a user view to make sure that a user is logged in and
    is in fact a user (i.e., has a UserProfile) before the
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
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return goto_home(*args, **kw)

        return view(*args, **kw)
            
    return wrapper


# And end-user who wants to edit his/her profile
@user_view
def edit_user_profile(request):
    if request.method=='POST':
        u=request.user

        # if we have separate user profiles set up we can probably use
        # the change paramenter function here.
        u.first_name=request.POST['first_name']
        u.last_name=request.POST['last_name']
        datestring = request.POST['date_of_birth']
        u.userprofile.date_of_birth = datetime.strptime(datestring, '%m/%d/%Y').date()
        if request.POST['sex']:
            u.userprofile.sex=request.POST['sex']
        u.save()
        u.userprofile.save()
        
        # Success message
        messages.add_message(request, messages.SUCCESS, "You have successfully updated your profile!")
        
        return HttpResponseRedirect(reverse("user_home"))

    else:
        n = request.user
        f = UserChangeForm()
        dob = n.userprofile.date_of_birth.strftime("%m/%d/%Y") if n.userprofile.date_of_birth else ""
        sex=n.userprofile.sex if n.userprofile.sex else ""
        return render_to_response('edit_user_profile.html',
                                  {'dob': dob,
                                   'sex':sex},
                                  context_instance=RequestContext(request))


# Trying to organize ratings by date created and grouping all ratings.
@user_view
def view_previous_responses(request):
    profile = request.user.userprofile
    feedback=profile.generalfeedback_set.all()
    rating=profile.rating_set.all()
    
    # rating_date is a dictionary of a list of all ratings on the same date
    rating_date={}
    for r in rating:

        # Check to see if there already is a rating on that date. If so, then just append the current rating to that list. Otherwise, create a new list with key as string of date
        date_string = r.date_created.strftime("%m/%d/%Y")
        if date_string in rating_date.keys():
            rating_date[date_string].append(r)
            rating_date[date_string].sort()
        else:
            rating_date[date_string]=[r]

    qs_responses=profile.questionresponse_set.all()
    response_date={}
    for q in qs_responses:
        date_string = q.date_created.strftime("%m/%d/%Y")
        if date_string in response_date.keys():
            response_date[date_string].append(q)
            response_date[date_string].sort()
        else:
            response_date[date_string]=[q]
    return render_to_response('user.html',
                              {'feedback':feedback,
                               'rating':rating,
                               'responses':qs_responses,
                               'rating_date':rating_date,
                               'response_date':response_date},
                              context_instance=RequestContext(request))



