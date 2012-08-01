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

    from_goog = urllib2.urlopen("https://maps.googleapis.com/maps/api/place/search/json?location="+str(lat)+","+str(lon)+"&radius="+str(settings.GOOGLE_PLACES_RADIUS)+"&sensor=true&key="+str(settings.GOOGLE_API_KEY))

    to_parse = json.loads(from_goog.read())
    business_list = []

    for entry in to_parse["results"]:
        business_list.append({
                "name":entry["name"],
                "types":entry["types"],
                "goog_id":entry["id"],
                "latitude":entry["geometry"]["location"]["lat"],
                "longitude":entry["geometry"]["location"]["lng"]
                })
        
    ret = json.dumps({'nearby_businesses':business_list})

    print business_list

    return HttpResponse(ret)

@mobile_view
@csrf_protect
def checkin(request):
    if request.method == 'POST':
        checkin_location = json.load(request)
	try:
	    business = BusinessProfile.objects.get(goog_id=checkin_location['goog_id'])
	except BusinessProfile.DoesNotExist:
            # Make an inactive business account
            print "exception found...."
            business = _make_inactive_business(checkin_location)

	return HttpResponse(json.dumps(business, cls=BusinessProfileEncoder))


def _make_inactive_business(checkin_location):
    # Function to make an inactive business, checkin_location is a JSON object
    # TODO: Implement
    business = BusinessProfile(business_name = '',
                               address = '',
                               goog_id=checkin_location['goog_id'],
                               latitude=float(checkin_location['latitude']),
                               longitude=float(checkin_location['longitude']))
    business_user =User.objects.create_user(username=checkin_location['name'],
                                            password='password')
    business_user.is_active = False
    business_user.save()
    business.user = business_user
    business.save()
    print "goog_id of business just created is...."+checkin_location['goog_id']
    print "about to create survey"
    survey = models.Survey(title='Feedback',
                           description='We would love to hear your thoughts on how we can improve our business.',
                           business=business)
    survey.save()
    
    #### TYPES:
    # 'TF': short text
    # 'TA': long text
    # 'RG': radio group
    # 'CG': checkbox
    
    # Generic question for (almost) every business.
    q0 = models.Question(label="What's one thing you would change about this business?", type='TA', options=[], survey=survey)
    q0.save()
    
    if "food" in checkin_location["types"] or "restaurant" in checkin_location["types"] and not 'grocery_or_supermarket' in checkin_location['types']:
        q1 = models.Question(label='What would you like to see on our menu?', type='TF', survey=survey)
        q1.save()
    elif "store" in checkin_location["types"] and not "grocery_or_supermarket" in checkin_location["types"]:
        q1 = models.Question(label='How helpful was our staff?', type='RG', options=['1','2','3','4','5'], survey=survey)
        q1.save()
    elif "grocery_or_supermarket" in checkin_location["types"]:
        q1 = models.Question(label='What products would you like to see more of here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What products would you start buying if the price were slightly lower?', type='TA', survey=survey)
        q2.save()
        q0.delete()
        q0 = models.Question(label="How do you feel this business could most improve?", type='TA', survey=survey)
        q0.save()
        
    elif 'amusement_park' in checkin_location['types']:
        q1 = models.Question(label='What is your favorite ride?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What food do you wish was served here?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='How can we make our line system more efficient?', type='TA', survey=survey)
        q3.save()
    elif 'aquarium' in checkin_location['types']:
        q1 = models.Question(label='What is your favorite animal at the aquarium?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What animal do you wish lived in the aquarium?', type='TF', survey=survey)
        q2.save()
        # Replace the default question.
        q0.delete()
        q0 = models.Question(label='How could your experience be improved?', type='TA', survey=survey)
        q0.save()
    elif 'bank' in checkin_location['types']:
        q1 = models.Question(label='How could your experience here be more efficient?', type='TA', survey=survey)
        q1.save()
        q2 = models.Question(label='What have you experienced at other banks that you wish this bank provided?', type='TA', survey=survey)
        q2.save()
    elif 'beauty_salon' in checkin_location['types']:
        q1 = models.Question(label='What product(s) do you wish you could buy here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What beauty technique(s) would you enjoy that are not provided here?', type='TA', survey=survey)
        q2.save()
    elif 'book_store' in checkin_location['types']:
        q1 = models.Question(label='What type of book would you like to see a larger selection for?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='If you started reading a new genre what would it be?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='In what ways do you think technology could improve the book store experience?', type='TA', survey=survey)
        q3.save()
        q4 = models.Question(label='What strategy do you recommend to ensure that bookstores stay exciting in modern culture?', type='TA', survey=survey)
        q4.save()
    elif 'bus_stop' in checkin_location['types']:
        q1 = models.Question(label='Do you have any friends that struggle to use the bus system because of a language barrier? What language do they speak?', type='TF', survey=survey)
        q1.save()
        # Replace the default question.
        q0.delete()
        q0 = models.Question(label='How could the bus system be more effective?', type='TA', survey=survey)
        q0.save()
    elif 'cafe' in checkin_location['types']:
        q1 = models.Question(label='What do you wish was served here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What music would you like to hear?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='What is your favorite part of other cafes that you recommend we adopt?', type='TA', survey=survey)
        q3.save()
    elif 'campground' in checkin_location['types']:
        q1 = models.Question(label='Is there anything dangerous around the grounds that should be attended to?', type='TA', survey=survey)
        q1.save()
        q2 = models.Question(label='How could the grounds be improved?', type='TF', survey=survey)
        q2.save()
    elif 'car_wash' in checkin_location['types']:
        q1 = models.Question(label='What have you seen at other car washes that you would like to see here?', type='TA', survey=survey)
        q1.save()
        q2 = models.Question(label='Do you think it is a good idea to have coffee and food sold here?', type='RF', options=["Yes","No"], survey=survey)
        q2.save()
    elif 'casino' in checkin_location['types']:
        q0.delete()
        q0 = models.Question(label='How could the casino experience be improved for you?', type='TF', survey=survey)
        q0.save()
        q1 = models.Question(label='Are there any games that you wish had more tables?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='Are there any machines that you would like to see carried?', type='TF', survey=survey)
        q2.save()
    elif 'cemetery' in checkin_location['types']:
        q1 = models.Question(label='Is there any way that you think technology could improve this cemetery?', type='TA', survey=survey)
        q1.save()
    elif 'city_hall' in checkin_location['types']:
        q1 = models.Question(label='Would you enjoy using your phone to browse city hall topics and for voting?', type='RG', options=["Yes","No"], survey=survey)
        q1.save()
        q2 = models.Question(label='What programs do you wish City Hall offered?', type='TA', survey=survey)
        q2.save()
    elif 'clothing_store' in checkin_location['types']:
        q1 = models.Question(label='What would you like to see carried here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='How do you think technology could improve your shoping experience here?', type='TA', survey=survey)
        q2.save()
        q3 = models.Question(label='What colors do you think should be highlighted next season?', type='TF', survey=survey)
        q3.save()
    elif 'dentist' in checkin_location['types']:
        q1 = models.Question(label='What reading material would you like provided for you?', type='TF', survey=survey)
        q1.save()
    elif 'department_store' in checkin_location['types']:
        q1 = models.Question(label='What would you like to see carried here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='How do you think technology could improve your shoping experience here?', type='TA',  survey=survey)
        q2.save()
        q3 = models.Question(label='What do you think are the best new  brands?', type='TF', survey=survey)
        q3.save()
    elif 'electronics_store' in checkin_location['types']:
        q1 = models.Question(label='What would you like to see carried here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='How do you think technology could improve your shoping experience here?', type='TA', survey=survey)
        q2.save()
        q3 = models.Question(label='What do you think are the best up and coming brands?', type='TF', survey=survey)
        q3.save()    
    elif 'food' in checkin_location['types']:
        q1 = models.Question(label='How could the food have been improved?', type='TA', survey=survey)
        q1.save()
        q2 = models.Question(label='What do you wish was served here?', type='TF', survey=survey)
        q2.save()
    elif 'furniture_store' in checkin_location['types']:
        q1 = models.Question(label='What price range do you want to see more of?', type='RG', options=['Low','Medium','High'], survey=survey)
        q1.save()
        q2 = models.Question(label='What brands and/or designs would you like carried here?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='How do you think technology could improve your shoping experience here?', type='TA', survey=survey)
        q3.save()
    elif 'gym' in checkin_location['types']:
        q1 = models.Question(label='What equiptment do you wish this gym provided?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='Are there any classes that you wish you could take at this gym?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='What food or drink products would you most like carried here?', type='TF', survey=survey)
        q3.save()
    elif 'hair_care' in checkin_location['types']:
        q1 = models.Question(label='What product(s) do you wish you could buy here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What beauty technique(s) would you enjoy that are not provided here?', type='TA', survey=survey)
        q2.save()
    elif 'health' in checkin_location['types']:
        q1 = models.Question(label='What improvements would you like to see in the waiting room?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='How could your experience here be more efficient?', type='TA', survey=survey)
        q2.save()
        q3 = models.Question(label='What reading material would you like provided for you?', type='TF', survey=survey)
        q3.save()
    elif 'hospital' in checkin_location['types']:
        q1 = models.Question(label='What improvements would you like to see in the waiting room?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='How could your experience here be more efficient?', type='TA', survey=survey)
        q2.save()
        q3 = models.Question(label='What reading material would you like provided for you?', type='TF', survey=survey)
        q3.save()
    elif 'laundry' in checkin_location['types']:
        q1 = models.Question(label='What could be improved about this location?', type='TA', survey=survey)
        q1.save()
        q2 = models.Question(label='How do you think technology could improve the experience here?', type='TA', survey=survey)
        q2.save()
    elif 'library' in checkin_location['types']:
        q1 = models.Question(label='How could finding the materials you came here for be made more efficient?', type='TA', survey=survey)
        q1.save()
        q2 = models.Question(label='What materials do you wish you could get here?', type='TA', survey=survey)
        q2.save()
    elif 'movie_theater' in checkin_location['types']:
        q1 = models.Question(label='What is your favorite movie theater and why?', type='TA', survey=survey)
        q1.save()
    elif 'night_club' in checkin_location['types']:
        q1 = models.Question(label='What music would you like to hear more of?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='How do you think technology could improve your experience here?', type='TA', survey=survey)
        q2.save()
        q3 = models.Question(label='What is your favorite night club and why?', type='TA', survey=survey)
        q3.save()
    elif 'park' in checkin_location['types']:
        q1 = models.Question(label='What artists would you enjoy public art from? Please give their name or website.', type='TA', survey=survey)
        q1.save()
        q2 = models.Question(label='Is there anything that needs maintenance here?', type='TA', survey=survey)
        q2.save()
    elif 'pharmacy' in checkin_location['types']:
        q1 = models.Question(label='What products would you like to see carried here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='If you would like more privacy involved in your pharmacy visit, what do you recommend?', type='TA', survey=survey)
        q2.save()
    elif 'post_office' in checkin_location['types']:
        q1 = models.Question(label='What kind of stamps would you like to start seeing sold here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='How could your visit to this post office be a more efficient process?', type='TA', survey=survey)
        q2.save()
    elif 'restaurant' in checkin_location['types']:
        q1 = models.Question(label='What is your favorite item on the menu?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What do you wish was served here?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='Do you have any comments on the service?', type='TA', survey=survey)
        q3.save()
        q4 = models.Question(label='If you were to create a special/discount plate, which menu items would you put on it?', type='TA', survey=survey)
        q4.save()
        q5 = models.Question(label='What music would you like to be playing here?', type='TF', survey=survey)
        q5.save()
    elif 'rv_park' in checkin_location['types']:
        q1 = models.Question(label='How do you think technology could be used to improve your experience at an rv park?', type='TA', survey=survey)
        q1.save()
        q2 = models.Question(label='Would you use a chat room for people currently visiting this rv park?', type='RG', options=['Yes','No'], survey=survey)
        q2.save()
    elif 'school' in checkin_location['types']:
        q1 = models.Question(label='How do you think technology could improve this school?', type='TA', survey=survey)
        q1.save()
        q0.delete()
        q0 = models.Question(label='What area would you most like to see improved here?', type='TF', survey=survey)
        q0.save()
        q2 = models.Question(label='What have been your favorite classes here?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='Who is your favorite teacher?', type='TF', survey=survey)
        q3.save()
        q4 = models.Question(label='What do you wish teachers did more of?', type='TA', survey=survey)
        q4.save()
        q5 = models.Question(label='What classes do you wish were offered here?', type='TF', survey=survey)
        q5.save()
    elif 'spa' in checkin_location['types']:
        q1 = models.Question(label='What product(s) do you wish you could buy here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What treatments would you enjoy that are not provided here?', type='TA', survey=survey)
        q2.save()
        q3 = models.Question(label='Who are you favorite employees here?', type='TF', survey=survey)
        q3.save()
        q4 = models.Question(label='What treatments do you think are going to become the next trends?', type='TA', survey=survey)
        q4.save()     
    elif 'stadium' in checkin_location['types']:
        q1 = models.Question(label='What food do you wish was served here?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='How do you think technology could improve your experience here?', type='TA', survey=survey)
        q2.save()
        q3 = models.Question(label='What is your favorite stadium and why?', type='TA', survey=survey)
        q3.save()
    elif 'subway_station' in checkin_location['types']:
        q1 = models.Question(label='Do you enjoy street musicians in the subway?', type='RG', options=['Yes','No'],  survey=survey)
        q1.save()
        q0.delete()
        q0 = models.Question(label='What would make you want to ride the subway more?', type='TA', survey=survey)
        q0.save()
        q2 = models.Question(label='Would you enjoy voting on potential advertisements for inside the subway?', type='RG', options=['Yes','No'], survey=survey)
        q2.save()
        q3 = models.Question(label='Would you like music to be played over speakers in a subway car?', type='RG', options=['Yes','No'], survey=survey)
        q3.save()
    elif 'train_station' in checkin_location['types']:
        q1 = models.Question(label='Do you enjoy street musicians in the train station?', type='RG', options=['Yes','No'], survey=survey)
        q1.save()
        q2 = models.Question(label='Would you enjoy voting on potential advertisements for trains and the station?', type='RG', options=['Yes','No'], survey=survey)
        q2.save()
        q3 = models.Question(label='Is there anything that needs maintenance?', type='TF', survey=survey)
        q3.save()
        q0.delete()
        q0 = models.Question(label='What would make you want to ride the train more?', type='TA', survey=survey)
        q0.save()
        q4 = models.Question(label='What food do you wish was served on the train?', type='TF', survey=survey)
        q4.save()
    elif 'university' in checkin_location['types']:
        q1 = models.Question(label='How do you think technology could improve this school?', type='TA', survey=survey)
        q1.save()
        q0.delete()
        q0 = models.Question(label='What area would you most like to see improved here?', type='TF', survey=survey)
        q0.save()
        q2 = models.Question(label='What have been your favorite classes here?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='Who is your favorite teacher?', type='TF', survey=survey)
        q3.save()
        q4 = models.Question(label='What do you wish teachers did more of?', type='TA', survey=survey)
        q4.save()
        q5 = models.Question(label='What classes do you wish were offered?', type='TF', survey=survey)
        q5.save()
        q6 = models.Question(label='What services do you think need to improve?', type='TA', survey=survey)
        q6.save()
    elif 'zoo' in checkin_location['types']:
        q1 = models.Question(label='What is your favorite animal at the zoo?', type='TF', survey=survey)
        q1.save()
        q2 = models.Question(label='What animal do you wish lived in the zoo?', type='TF', survey=survey)
        q2.save()
        q3 = models.Question(label='What activities do you wish were provided here?', type='TF', survey=survey)
        q3.save()
        q0.delete()
        q0 = models.Question(label='How could your experience be improved?', type='TA', survey=survey)
        q0.save()
        q4 = models.Question(label='What do you wish teachers did more of?', type='TA', survey=survey)
        q4.save()
        q5 = models.Question(label='How do you think technology could improve the zoo?', type='TA', survey=survey)
        q5.save()
    else:
        q1 = models.Question(label='Rate your overall experience:',  type='RG', options=['1','2','3','4','5'], survey=survey)
        q1.save()
    return business

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
    data = json.load(request)
    business_id = data['business_id']
    business = models.BusinessProfile.objects.get(id=business_id)
    survey = business.survey_set.all()[0]
    
    questions = []
    qe = QuestionEncoder()
    qs = survey.question_set.all()
    for question in qs:
        if question.active:
            new_question = qe.default(question)
            questions.append(new_question)

    print questions
    return HttpResponse(json.dumps(survey, cls=SurveyEncoder))

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
    return HttpResponse('body: %s' % request.body)
    sys.stderr.write('keys %s' % request.FILES.keys())
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
