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
import employee_views
import business_views
from registration import forms as registration_forms
import settings
import datetime

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
                                             'user_type': user_type},
                              context_instance=RequestContext(request))

# Encodes a RatingProfile into JSON format
class RatingProfileEncoder(json.JSONEncoder):
    def default(self, o):
	if isinstance(o, models.RatingProfile):
            dim_enc = RatedDimensionEncoder()
	    res = {'title': o.title,
                   'dimensions': [dim_enc.default(dim) for dim in o.rateddimension_set.all()],
                   'business_id': o.business.id,
                   'id':o.id }
	    return res
	else:
	    return json.JSONEncoder.default(self, o)

class RatedDimensionEncoder(json.JSONEncoder):
    def default(self, o):
	if isinstance(o, models.RatedDimension):
            return {'title': o.title,
                    'active': o.is_active,
                    'is_text': o.is_text,
                    'id':o.id}
	else:
	    return json.JSONEncoder.default(self, o)

# Encodes an Employee into JSON format
class EmployeeEncoder(json.JSONEncoder):
    def default(self, o):
	if isinstance(o, models.EmployeeProfile):
            dimension_encoder = RatedDimensionEncoder()
            dimension_list = []
            for d in o.rating_profile.rateddimension_set.all():
                dimension_list.append(dimension_encoder.default(d))
            image_url = settings.SERVER_URL+settings.MEDIA_URL+employee_views._profile_picture(o)
	    res = {'first_name':o.user.first_name,
		   'last_name':o.user.last_name,
		   'bio':o.bio,
		   'ratings':
		       {'rating_title':"" if o.rating_profile.title is None else o.rating_profile.title,
			'dimensions':dimension_list},
                   'image':image_url,
                   'id':o.id
		   }
	    return res
	else:
	    return json.JSONEncoder.default(self, o)

# Encodes a UserProfile into JSON format
class UserProfileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.UserProfile):
            return {'first_name':o.user.first_name,
                    'last_name':o.user.last_name,
                    'birth':o.date_of_birth.strftime("%d/%m/%Y"),
                    'id':o.id}
        else:
            return json.JSONEncoder.default(self, o)

# Encodes a BusinessProfile into JSON format
class BusinessProfileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.BusinessProfile):
            bus_user = o.user
            logo_url = '%s%s' % (settings.MEDIA_URL, settings.DEFAULT_PROFILE_IMAGE)
            if o.logo:
                logo_url = o.logo.url
            res = {'name': bus_user.username,
                   'goog_id': o.goog_id,
                   'business_id': o.id,
                   'latitude': o.latitude,
                   'longitude': o.longitude,
                   'phone': o.phone,
                   'logo': logo_url}
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

# Encodes a NewsFeedItem into JSON.
class NewsFeedItemEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.NewsFeedItem):
            image_url = '%s%s' % (settings.MEDIA_URL, settings.DEFAULT_PROFILE_IMAGE)
            if o.image:
                image_url = o.image.url
            return {'id': o.id,
                    'title': o.title,
                    'subtitle': o.subtitle,
                    'body': o.body,
                    'date': o.date.strftime('%m/%d/%Y'),
                    'business': o.business.business_name,
                    'image': image_url,
                    'date_edited':o.date_edited.strftime('%m/%d/%Y')}
        else:
            return json.JSONEncoder.default(self, o)

class RatingEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Rating):
            return {'value':o.rating_value,
                    'user':UserProfileEncoder().default(o.user),
                    'date':o.date_created.strftime("%d/%m/%Y"),
                    'title':o.title}
        else:
            return json.JSONEncoder.default(self, o)
