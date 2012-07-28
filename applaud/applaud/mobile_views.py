from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile, RatedDimension, Rating
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
from applaud.models import UserProfile
from registration import forms as registration_forms
from views import BusinessProfileEncoder, EmployeeEncoder, SurveyEncoder, QuestionEncoder, NewsFeedItemEncoder, BusinessPhotoEncoder
from business_views import save_image
from django.utils.timezone import utc

# 'mobile_view' decorator.
def mobile_view(view):
    '''
    Checks a MobileView to make sure that a user is logged in and
    is in fact an end-user (i.e., has a UserProfile) before the
    view is executed. If either of these tests fail, the user is redirected
    to the appropriate page.
    '''
    def goto_login(*args, **kw):
        return HttpResponseForbidden("ERROR: not authenticated")

    def goto_home(*args, **kw):
        return HttpResponseForbidden("ERROR: no profile")

    def get_csrf(*args, **kw):
        return HttpResponse(get_token(args[0]))

    def wrapper(*args, **kw):
        request = args[0]
        if not request.user.is_authenticated():
            return goto_login(*args, **kw)
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return goto_home(*args, **kw)

        if request.method == 'GET':
            return get_csrf(*args, **kw)

        return view(*args, **kw)
            
    return wrapper

# IOS notifies us of where device is. We return business locations.
def whereami(request):
    if not "latitude" in request.GET or not  "longitude" in request.GET:
	# error = "Latitude & longitude confusion...."
	# return render_to_response('error.html',{"error":error})
        return HttpResponse(get_token(request))

    lat = request.GET["latitude"]
    lon = request.GET["longitude"]	

    from_goog = urllib2.urlopen("https://maps.googleapis.com/maps/api/place/search/json?location="+str(lat)+","+str(lon)+"&radius="+str(settings.GOOGLE_PLACES_RADIUS)+"&sensor=true&key="+settings.GOOGLE_API_KEY)

    to_parse = json.loads(from_goog.read())

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

@mobile_view
@csrf_protect
def checkin(request):
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

# Getting and posting employee data from iOS.
@mobile_view
@csrf_protect
def evaluate(request):
    '''evaluate

    This is the view that accepts rating data from end-users and
    rates an employee of a business per that employee's RatingProfile.
    '''
    rating_data = json.load(request)
    print rating_data

    if 'employee' in rating_data:
        try:
            e = EmployeeProfile.objects.get(id=rating_data['employee']['id'])
        except EmployeeProfile.DoesNotExist:
            pass
        for key, value in rating_data['ratings'].iteritems():
            rated_dimension = RatedDimension.objects.get(id=key)
            if rated_dimension.is_text:
                r = Rating(title=rated_dimension.title,
                           rating_text=value,
                           employee=e,
                           dimension=rated_dimension,
                           date_created=datetime.utcnow().replace(tzinfo=utc),
                           user=request.user.userprofile)
            else:
                r = Rating(title=rated_dimension.title,
                           rating_value=float(value),
                           employee=e,
                           dimension=rated_dimension,
                           date_created=datetime.utcnow().replace(tzinfo=utc),
                           user=request.user.userprofile)
            r.save()
    return HttpResponse("") # Empty response = all went well

@mobile_view
@csrf_protect
def employee_list(request):
    '''List the employees by last name and first name, according
    to the business id which is passed as JSON.

    This is used by mobile devices to view all the employees for a business.
    '''
    business_id = json.load(request)['business_id']
    business = models.BusinessProfile(id=business_id)
    return HttpResponse(json.dumps(list(business.employeeprofile_set.all()),
                                   cls=EmployeeEncoder))

@mobile_view
@csrf_protect
def get_survey(request):
    '''Gets the survey for a particular business, the ID of
    which is passed in as JSON.
    '''
    business_id = json.load(request)['business_id']
    business = models.BusinessProfile(id=business_id)
    print 'business_id: %s' % business_id
    survey = business.survey_set.all()[0]
    print survey
    questions = []
    qe = QuestionEncoder()
    for question in survey.question_set.all():
        if question.active:
            questions.append(qe.default(question))
    print survey.title
    print survey.description
    print questions
    return HttpResponse(json.dumps({'title': survey.title,
                                    'description': survey.description,
                                    'questions': questions}))

# Posting survey response.
@mobile_view
@csrf_protect
def survey_respond(request):
    '''survey_respond

    This is the view that accepts a response to a survey for a particular
    business from the end-user.
    '''
    for answer in json.load(request)['answers']:
        question = models.Question.objects.get(id=answer['id'])
        response = answer['response']
        qr = models.QuestionResponse(question=question, response=response,
                                     date_created=datetime.utcnow().replace(tzinfo=utc),
                                     user=request.user.userprofile)
        qr.save()
    return HttpResponse("")

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
    keith = models.BusinessProfile.objects.get(id=3)
    res = { "nearby_businesses":
        	[BusinessProfileEncoder().default(keith)],
            }
    return HttpResponse(json.dumps(res))

# General feedback.
@mobile_view
@csrf_protect
def general_feedback(request):
    answer_data = json.load(request)
    feedback = models.GeneralFeedback(feedback=answer_data['answer'],
                                      business=models.BusinessProfile.objects.get(id=answer_data['business_id']),
                                      user=request.user.userprofile,
                                      date_created=datetime.utcnow().replace(tzinfo=utc))
    feedback.save()
    return HttpResponse("")

@mobile_view
@csrf_protect
def nfdata(request):
    business_id = json.load(request)['business_id']
    business = models.BusinessProfile(id=business_id)
    nfitems = business.newsfeeditem_set.all()
    nfitem_list = []
    encoder = NewsFeedItemEncoder()
    for nfitem in nfitems:
        nfitem_list.append(encoder.default(nfitem))
    ret = {'newsfeed_items':nfitem_list}
    return HttpResponse(json.dumps(ret))

@csrf_protect
@mobile_view
def post_photo(request):
    """
    Post a photo from the phone to the server. Called
    with a POST.
    
    Expects 'business_id' and 'tags' as POST keys, and
    'image' as a file.
    """
    profile = request.user.userprofile
    image = request.FILES['image']
    business = models.BusinessProfile.objects.get(id=request.POST['business_id'])
    business_photo = models.BusinessPhoto(business=business,
                                          tags=json.loads(request.POST['tags']),
                                          uploaded_by=profile)
    business_photo.save()
    filename = '%s_%s.jpg' % (profile.id,
                       business.business_name)
    save_image(business_photo.image, filename, image)
    return HttpResponse('')

#@mobile_view
def get_photos(request):
    """
    Get all the photos associated with a particular business,
    whose database ID is passed in by GET.
    """
    business = models.BusinessProfile.objects.get(id=int(request.GET['id']))
    encoder = BusinessPhotoEncoder()
    return HttpResponse(json.dumps({'photos': [encoder.default(photo) for photo in business.businessphoto_set.all()]}))
