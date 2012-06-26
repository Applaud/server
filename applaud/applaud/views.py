from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile
from django.template import RequestContext, Template
from django.contrib.auth.forms import UserCreationForm
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

def index(request):
    username = ""
    profile = ""
    if request.user.is_authenticated():
	# Are we a business?
	try:
	    profile = request.user.businessprofile
	except BusinessProfile.DoesNotExist:
	    pass
	username = request.user.username
    
    return render_to_response('index.html',{'username':username,'profile':profile})

# Do we need this?
@csrf_protect
def create_employee(request):
    if request.user.is_authenticated():
        #Are we a business?
        try:
            profile=request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseRedirect("/accounts/login/")

        username=request.user.username
    else:
        return HttpResponseRedirect("/accounts/login/")

    # if  request.method == 'POST':
    #     employee_form = forms.EmployeeForm(request.POST)
    #     e=employee_form.save(commit=False)
    #     e.business= profile
    #     e.save()
        
    employees = profile.employeeprofile_set.all()

    return render_to_response('employees.html',
                              {'list':employees},
                              context_instance=RequestContext(request))

# Encodes an Employee into JSON format
class EmployeeEncoder(json.JSONEncoder):
    def default(self, o):
	if isinstance(o, models.EmployeeProfile):
	    dimensions = o.rating_profile.dimensions
	    res = {'first_name':o.user.first_name,
		   'last_name':o.user.last_name,
		   'bio':o.bio,
		   'ratings':
		       {'rating_title':"" if o.rating_profile.title is None else o.rating_profile.title,
			'dimensions':dimensions}
		   }
	    return res
	else:
	    return json.JSONEncoder.default(self, o)

# Encodes a BusinessProfile into JSON format
class BusinessProfileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.BusinessProfile):
            bus_user = o.user
            res = {'name':bus_user.username,
                   'goog_id':o.goog_id,
                   'business_id':o.id,
                   'latitude':o.latitude,
                   'longitude':o.longitude,
                   'phone':o.phone}
            return res
        else:
            return json.JSONEncoder.default(self, o)

# Encodes a Survey into JSON format
class SurveyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Survey):
            question_list = list(o.question_set.all())
            questions = []
            for q in question_list:
                questions.append({'label': q.label,
                                  'type': q.type,
                                  'options': q.options,
                                  'id': q.id})
            res = {'title': o.title,
                   'description': o.description,
                   'questions': questions}
            return res
        else:
            return json.JSONEncoder.default(self, o)
