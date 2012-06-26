from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile
from django.template import RequestContext, Template
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from datetime import datetime
from django.contrib.auth.models import Group, User
import sys
import json
import urllib2
from applaud import forms
from applaud import models
from registration import forms as registration_forms


# And end-user who wants to edit his/her profile
def edit_user_profile(request):
    if request.user.is_authenticated():
        if request.method=='POST':
            u=request.user
            # if we have separate user profiles set up we can probably use the change paramenter function here.
            u.first_name=request.POST['first_name']
            u.last_name=request.POST['last_name']
            u.save()
            return render_to_response('user.html',
                                      context_instance=RequestContext(request))
        else:
            n = request.user
            f = UserChangeForm()
            return render_to_response('edit_user_profile.html', 
                                      context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/fail/")


def view_previous_responses(request):
    if request.user.is_authenticated():
        try:
            profile = request.user.userprofile
        except BusinessProfile.DoesNotExist:
            return render_to_response('fail.html',
                                      {'debug': "You're not signed in as an end-user!"},
                                      context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')

    feedback=profile.generalfeedback_set.all()
    rating=profile.rating_set.all()
    qs_responses=profile.questionresponse_set.all()
    

    return render_to_response('user.html',
                              {'feedback':feedback,
                               'rating':rating,
                               'responses':qs_responses},
                              context_instance=ReqeustContext(request))
