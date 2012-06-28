from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import BusinessProfile, EmployeeProfile
from django.template import RequestContext, Template
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
        sys.stderr.write('date: %s\n\n' % str(u.userprofile.date_of_birth))
        u.save()
        u.userprofile.save()

        return HttpResponseRedirect(reverse("user_home"))

    else:
        n = request.user
        f = UserChangeForm()
        dob = n.userprofile.date_of_birth.strftime("%m/%d/%Y") if n.userprofile.date_of_birth else ""
        return render_to_response('edit_user_profile.html',
                                  {'dob': dob},
                                  context_instance=RequestContext(request))

@user_view
def view_previous_responses(request):
    profile = request.user.userprofile
    feedback=profile.generalfeedback_set.all()
    rating=profile.rating_set.all()
    qs_responses=profile.questionresponse_set.all()
    
    return render_to_response('user.html',
                              {'feedback':feedback,
                               'rating':rating,
                               'responses':qs_responses},
                              context_instance=ReqeustContext(request))
