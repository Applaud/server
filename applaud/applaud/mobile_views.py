from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile
from django.template import RequestContext, Template
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from datetime import datetime
from django.contrib.auth.models import Group, User
import settings
import sys
import json
import urllib2
from applaud import forms
from applaud import models
from registration import forms as registration_forms
from views import BusinessProfileEncoder, EmployeeEncoder

# IOS notifies us of where device is. We return business locations.
def whereami(request):
    if not "latitude" in request.GET or not  "longitude" in request.GET:
	# error = "Latitude & longitude confusion...."
	# return render_to_response('error.html',{"error":error})
        return HttpResponse(get_token(request))

    lat = request.GET["latitude"]
    lon = request.GET["longitude"]	

    from_goog = urllib2.urlopen("https://maps.googleapis.com/maps/api/place/search/json?location="+lat+","+lon+"&radius="+settings.GOOGLE_PLACES_RADIUS+"&sensor=true&key="+settings.GOOGLE_API_KEY)

    to_parse = json.loads(from_goog.read())
	#return HttpResponse(to_parse)

    business_list = []

    for entry in to_parse["results"]:
	# Create an inactive Applaud account for any businesses we don't recognize here.
        business_list.append(
            {
                "name":entry["name"],
                "type":entry["types"][0],
                "goog_id":entry["id"],
                "latitude":entry["geometry"]["location"]["lat"],
                "longitude":entry["geometry"]["location"]["lng"]
                })
        
    ret = json.dumps({'nearby_businesses':business_list})
    return HttpResponse(ret)

@csrf_protect
def checkin(request):
    # if not request.user.is_authenticated():
    #     return HttpResponseForbidden("")
    if request.method == 'POST':
        checkin_location = json.load(request)
	try:
	    business = BusinessProfile.objects.get(goog_id=checkin_location['goog_id'])
	except BusinessProfile.DoesNotExist:
	    business = BusinessProfile(goog_id=checkin_location['goog_id'],
				       latitude=float(checkin_location['latitude']),
				       longitude=float(checkin_location['longitude']))
	    business_user = User.objects.create_user(username=checkin_location['name'],
						     password='password')
            business_user.is_active = False
	    business_user.save()
	    business.user = business_user
	    business.save()

	return HttpResponse(json.dumps(business, cls=BusinessProfileEncoder))
    else:
        sys.stderr.write("---------------------------------------- giving csrf")
        return HttpResponse(get_token(request))

# Getting and posting employee data from iOS.
@csrf_protect
def evaluate(request):
    '''evaluate

    This is the view that accepts rating data from end-users and
    rates an employee of a business per that employee's RatingProfile.
    '''
    if request.user.is_authenticated():
        if request.method != 'POST':
            return HttpResponse(get_token(request))
        rating_data = json.load(request)
        if 'employee' in request.POST:
            try:
                e = EmployeeProfile.objects.get(rating_data['employee']['id'])
            except EmployeeProfile.DoesNotExist:
                pass
            for key, value in rating_data['ratings']:
                r = Rating(title=key, rating_value=float(value),employee=e,date_created=datetime.now())
                r.save()
    return HttpResponse('foo')

@csrf_protect
def employee_list(request):
    '''List the employees by last name and first name, according
    to the business id which is passed as JSON.

    This is used by mobile devices to view all the employees for a business.
    '''
    if request.user.is_authenticated():
        if request.method == 'GET':
            return HttpResponse(get_token(request))
        business_id = json.load(request)['business_id']
        business = models.BusinessProfile(id=business_id)
        return HttpResponse(json.dumps(list(business.employeeprofile_set.all()),
                                       cls=EmployeeEncoder))
    return HttpResponseForbidden("end-user not authenticated")

# Posting survey response.
@csrf_protect
def survey_respond(request):
    '''survey_respond

    This is the view that accepts a response to a survey for a particular
    business from the end-user.
    '''
    if request.user.is_authenticated():
        if request.method != 'POST':
            return HttpResponse(get_token(request))
        for answer in json.load(request)['answers']:
            question = models.Question.objects.get(id=answer['id'])
            response = answer['response']
            qr = models.QuestionResponse(question=question, response=response, date_created=datetime.now())
            qr.save()
    return HttpResponse('foo')

# Static JSON data that can be used for testing when the internet's down
def example(request):
    res = { "nearby_businesses": [] }
    return HttpResponse(json.dumps(res))

def example2(request):
    res = { "nearby_businesses": [
	    {"name":"Foo Burgers",
	     "type":"Burgers",
	     "goog_id":"677679492a58049a7eae079e0890897eb953d79b",
	     "latitude":39.981634,
	     "longitude":-83.004617},
	    ]
	    }
    return HttpResponse(json.dumps(res))

def example3(request):
    res = { "nearby_businesses":
		[
	    {"name":"Foo Burgers",
	     "type":"Burgers",
	     "goog_id":"677679492a58049a7eae079e0890897eb953d79b",
	     "latitude":39.981634,
	     "longitude":-83.004617,
             "id": 1},
	    {"name":"Seymour House of Smiles",
	     "type":"Orthodontist",
	     "goog_id":"27ea39c8fed1c0437069066b8dccf958a2d06f19",
	     "latitude":39.981934,
             "longitude":-83.004676,
             "id": 1}, # ids are the same for testing purposes...
	    ],
	    }
    return HttpResponse(json.dumps(res))

# General feedback.
@csrf_protect
def general_feedback(request):
    if request.user.is_authenticated():
        if request.method != 'POST':
                return HttpResponse(get_token(request))
        answer_data = json.load(request)
        feedback = models.GeneralFeedback(feedback=answer_data['answer'],
                                          business=models.BusinessProfile.objects.get(id=answer_data['business_id']),
                                          date_created=datetime.now())
        feedback.save()
        return HttpResponse('foo')
    return HttpResponseForbidden("end-user not authenticated")

# Getting the CSRF token for mobile devices
def get_csrf(request):
    return HttpResponse(get_token(request))
