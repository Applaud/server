from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile
from django.core.urlresolvers import reverse
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
    user_type = ''
    profile = ""
    if request.user.is_authenticated():
	# Are we a business?
	try:
	    profile = request.user.businessprofile
            user_type = 'business'
	except BusinessProfile.DoesNotExist:
	    try:
                profile = request.user.employeeprofile
                user_type = 'employee'
            except EmployeeProfile.DoesNotExist:
                user_type = 'user'
    return render_to_response('index.html', {'user': request.user,
                                             'user_type': user_type})

# Encodes a RatingProfile into JSON format
class RatingProfileEncoder(json.JSONEncoder):
    def default(self, o):
	if isinstance(o, models.RatingProfile):
	    res = {'title':o.title,
                   'dimensions':o.dimensions,
                   'business_id':o.business.id,
                   'id':o.id }
	    return res
	else:
	    return json.JSONEncoder.default(self, o)

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
			'dimensions':dimensions},
                   'id':o.id
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
            question_encoder = QuestionEncoder()
            for q in question_list:
                questions.append(question_encoder.default(q))
            res = {'title': o.title,
                   'description': o.description,
                   'questions': questions}
            return res
        else:
            return json.JSONEncoder.default(self, o)

# Encodes a Question into JSON.
class QuestionEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Question):
            return {'label': o.label,
                    'type': o.type,
                    'options': o.options,
                    'active': o.active,
                    'id': o.id}
        else:
            return json.JSONEncoder.default(self, o)
