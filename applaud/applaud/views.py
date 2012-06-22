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

def whereami(request):
    if not "latitude" in request.GET or not  "longitude" in request.GET:
	# error = "Latitude & longitude confusion...."
	# return render_to_response('error.html',{"error":error})
        return HttpResponse(get_token(request))

    lat = request.GET["latitude"]
    lon = request.GET["longitude"]	

    goog_api_key="AIzaSyCbw9_6Mokk_mKwnH02OYyB6t5MrepFV_E"
    radius="100"

    from_goog = urllib2.urlopen("https://maps.googleapis.com/maps/api/place/search/json?location="+lat+","+lon+"&radius="+radius+"&sensor=false&key="+goog_api_key)

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

# This allows a user to save and view newsfeed posts
@csrf_protect
def newsfeed_create(request):
    #What happens if an employee or end-user visits this page?
    if request.user.is_authenticated():
	# Are we a business?
	try:
	    profile = request.user.businessprofile
	except BusinessProfile.DoesNotExist:
	    return HttpResponseNotFound('Could not find requested page.')

	username = request.user.username

    else:
        return HttpResponseRedirect('/accounts/login/')

    if request.method == 'POST':
	n = forms.NewsFeedItemForm(request.POST)
	newsitem = n.save(commit=False)
	newsitem.date = datetime.now()
	newsitem.date_edited = datetime.now()
        newsitem.business = profile
	newsitem.save()
    
    f = forms.NewsFeedItemForm()
    newsfeed = profile.newsfeeditem_set.all()
	
    return render_to_response('basic_newsfeed.html',
				  {'form':f, 'list':newsfeed},
				  context_instance=RequestContext(request))
    
# Delete a newsfeed item
@csrf_protect
def delete_newsfeed_item(request):
    if request.user.is_authenticated():
	# Are we a business?
	try:
	    profile = request.user.businessprofile
	except BusinessProfile.DoesNotExist:
	    pass
        
    else:
        return HttpResponseRedirect('/accounts/login')  

    #Business is authenticated

    #Request is POST - Business has selected and confirmed news feed item deletion
    if request.method == 'POST':
	n = models.NewsFeedItem.objects.get(pk=request.POST['id'])
	n.delete()
	
        f = forms.NewsFeedItemForm()
        newsfeed = profile.newsfeeditem_set.all()
	
        return render_to_response('basic_newsfeed.html',
				  {'form':f, 'list':newsfeed},
				  context_instance=RequestContext(request))

    #Request is GET - Send to confirmation page
    else:
	n = models.NewsFeedItem.objects.get(pk=request.GET['id'])
	return render_to_response('delete_confirmation.html',
				  {'item':n, 'id':request.GET['id']},
				  context_instance=RequestContext(request))

#Serves the newsfeed to iOS
@csrf_protect
def nfdata(request):
    if request.method == 'GET':
        return HttpResponse(get_token(request))
    if request.user.is_authenticated():
        business_id = json.load(request)['business_id']
        business = models.BusinessProfile(id=business_id)
        nfitems = business.newsfeeditem_set.all()
        nfitem_list = []
        for nfitem in nfitems :
            nfitem_list.append({'title':nfitem.title,
                                'subtitle':nfitem.subtitle,
                                'body':nfitem.body,
                                'date':nfitem.date.strftime('%Y-%m-%d %I:%M')})

        ret = { 'newsfeed_items':nfitem_list }

        return HttpResponse(json.dumps(ret))
    
    return HttpResponseForbidden("end-user not authenticated")

@csrf_protect
def edit_newsfeed(request):
    if request.user.is_authenticated():
        #Are we a business?
        try:
            profile=request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseNotFound("Could not find the requested page.")

        username=request.user.username
    else:
        return HttpResponseRedirect("/accounts/login/")

    if request.method == 'POST':	
	n = models.NewsFeedItem.objects.get(pk=request.POST['id'])
	d = {'title':request.POST['title'],
	     'subtitle':request.POST['subtitle'],
	     'body':request.POST['body'],
             'date_edited':datetime.now()}
	
	n.change_parameters(d)
	n = n.save()

	f = forms.NewsFeedItemForm()
	newsfeed = profile.newsfeeditem_set.all()
	return render_to_response('basic_newsfeed.html',
				  {'form':f, 'list':newsfeed},
				  context_instance=RequestContext(request))

    else:
	try:                        
	    n = models.NewsFeedItem.objects.get(pk=request.GET['id'])
	except:
	    return render_to_response('fail.html', {}, context_instance=RequestContext(request))

                #this might be a tad sloppy
	d = dict((key, value) for key, value in n.__dict__.iteritems() if not callable(value) and not key.startswith('_'))
	
	f = forms.NewsFeedItemForm(initial=d)
       	
	return render_to_response('edit_newsfeed.html',
				  {'form':f, 'id':request.GET['id']},
				  context_instance=RequestContext(request))

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


@csrf_protect
def delete_employee(request):
    if request.user.is_authenticated():
        #Are we a business?
        try:
            profile=request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseNotFound("Could not find the requested page.")

        username=request.user.username
    else:
        return HttpResponseRedirect("/accounts/login/")

    if request.method == 'POST':
        emp = models.Employee.objects.get(pk=request.POST['id'])
        emp.delete()
        
        new_form = forms.EmployeeForm()
        employees = profile.employee_set.all()

        return render_to_response('employees.html',
                                  {'form': new_form, 'list': employees},
                                  context_instance=RequestContext(request))
    else:
        emp = models.Employee.objects.get(pk=request.GET['id'])
        return render_to_response('delete_employee_confirmation.html', {'employee':emp, 'id':request.GET['id']}, context_instance=RequestContext(request))


    
@csrf_protect
def edit_employee(request):
    if request.user.is_authenticated():
    #Are we a business?
        try:
            profile=request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseNotFound("Could not find the requested page.")

        username=request.user.username
    else:
        return HttpResponseRedirect("/accounts/login/")

    if request.method == 'POST':	
        n = models.Employee.objects.get(pk=request.POST['id'])
	d = {'first_name':request.POST['first_name'],
	     'last_name':request.POST['last_name'],
	     'bio':request.POST['bio']}
	
	n.change_parameters(d)
	n = n.save()

	f = forms.EmployeeForm()
	emp = profile.employee_set.all()
	return render_to_response('employees.html',
				  {'form':f, 'list':emp},
				  context_instance=RequestContext(request))
    # request method is GET
    else:
	try:                        
            n = models.Employee.objects.get(pk=request.GET['id'])
	except:
	    return render_to_response('fail.html', {}, context_instance=RequestContext(request))

                #this might be a tad sloppy
	d = dict((key, value) for key, value in n.__dict__.iteritems() if not callable(value) and not key.startswith('_'))
	
	f = registration_forms.EmployeeRegistrationForm(initial=d)
       	
	return render_to_response('edit_employee.html',
				  {'form':f, 'id':request.GET['id']},
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

        sys.stderr.write(str(success_chart))

        # Return string for rendering in google charts
        return render_to_response('employee_stats.html',
                                  {'chartdata':json.dumps( success_chart ),
                                   'employee':employee})

                                   
    return HttpResponseForbidden("employee not logged in")
        

@csrf_protect
def create_rating_profile(request):
    '''Create a rating profile.
    Takes a variable number of text fields and turns them into dimensions
    for a rating profile. Also includes the title.
    '''
    if request.method == 'GET':
        # Be sure we're logged in and that we're a business.
        if request.user.is_authenticated() and 'businessprofile' in dir(request.user):
            return render_to_response('/business/create_rating_profile.html',
                                      {},
                                      context_instance=RequestContext(request))
        else:
            return HttpResponseNotFound("Could not find the requested page.",
                                        context_instance=RequestContext(request))
    if request.method == 'POST':
	sys.stderr.write(str(request.POST))
        if request.user.is_authenticated():
            try:
                profile = request.user.businessprofile
            except BusinessProfile.DoesNotExist:
                return HttpResponseNotFound("Could not find the requested page.",
                                            context_instance=RequestContext(request))

        else:
            return HttpResponseNotFound("Could not find the requested page.",
                                        context_instance=RequestContext(request))

        i = 0
        dimensions = []
        while 'dimension_' + str(i) in request.POST and request.POST['dimension_' + str(i)]:
            dimensions.append(request.POST['dimension_' + str(i)])
            i += 1
        title = ''
        if 'title' in request.POST and request.POST['title']:
            title = request.POST['title']
        errors = {}
        err = False
        if not title:
            errors['title_err'] = "You should enter a title for this rating profile."
            err = True
        if not dimensions:
            errors['dimensions_err'] = "No dimensions?"
            err = True
        if err:
            errors['dimensions'] = dimensions
            return render_to_response('/business/create_rating_profile.html',
                                      errors,
                                      context_instance=RequestContext(request))
        rp = RatingProfile(title=title, dimensions=dimensions, business=profile)
        rp.save()
	
        return HttpResponseRedirect('/business/ratingprofiles')

@csrf_protect
def list_rating_profiles(request):
    # Make sure we're a business.
    if not (request.user.is_authenticated() and 'businessprofile' in dir(request.user)):
        return render_to_response('fail.html')
    business = request.user.businessprofile
    l = list(business.ratingprofile_set.all())
    ret = []
    for item in l:
	ap = {}
	ap['title']=item.title
	ap['dimensions']=item.dimensions
	ret.append(ap)
    return render_to_response('employeeprofile_create.html',
				  {'list':ret},
				  context_instance=RequestContext(request))

@csrf_protect
def create_survey(request):
    '''Create a survey.
    Takes a variable number of text fields and turns them into questions
    for a survey. Also includes the title and description.
    '''
    if request.method == 'GET':
        # Be sure we're logged in and that we're a business.
        if request.user.is_authenticated() and 'businessprofile' in dir(request.user):
            return render_to_response('survey_create.html',
                                      {},
                                      context_instance=RequestContext(request))
        else:
            return render_to_response('fail.html')
    if request.method == 'POST':
	sys.stderr.write(str(request.POST))
        if request.user.is_authenticated():
            try:
                profile = request.user.businessprofile
            except BusinessProfile.DoesNotExist:
                return render_to_response('fail.html')
        else:
            return HttpResponseRedirect('/accounts/business/')
        i = 0
        questions = []
        while 'question_' + str(i) in request.POST and request.POST['question_' + str(i)]:
	    options = []
	    j = 0
	    optionFieldName='question_'+str(i)+"_option_"+str(j)
	    while optionFieldName in request.POST and request.POST[optionFieldName]:
		options.append(request.POST[optionFieldName])
		j += 1
		optionFieldName='question_'+str(i)+"_option_"+str(j)

	    questions.append({'title':request.POST['question_' + str(i)],
			      'type':request.POST['question_' +str(i)+"_type"],
			      'options':json.dumps(options)})
            i += 1
	    
        title = description = ''
        if 'title' in request.POST and request.POST['title']:
            title = request.POST['title']
        if 'description' in request.POST and request.POST['description']:
            description = request.POST['description']
        errors = {}
        err = False
        if not title:
            errors['title_err'] = "You should enter a title for this survey."
            err = True
        if not questions:
            errors['questions_err'] = "No questions?"
            err = True
        if err:
            errors['questions'] = questions
            return render_to_response('survey_create.html',
                                      errors,
                                      context_instance=RequestContext(request))
        # Which business are we?
        business = BusinessProfile.objects.get(user=request.user)
	# First, create the Survey
	s = models.Survey(title=title, description=description, business=business)
	s.save()

	# Create each of the questions on the Survey
	for question in questions:
	    q = models.Question(label=question['title'],
				type=question['type'],
				options= question['options'],
				survey=s)
	    q.save()

        return HttpResponseRedirect('/business/survey_create')	

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

@csrf_protect
def get_survey(request):
    '''Gets the survey for a particular business, the ID of
    which is passed in as JSON.
    '''
    if request.user.is_authenticated():
        if request.method == 'GET':
            return HttpResponse(get_token(request))
        business_id = json.load(request)['business_id']
        business = models.BusinessProfile(id=business_id)
        return HttpResponse(json.dumps(list(business.survey_set.all())[0],
                                       cls=SurveyEncoder))
    return HttpResponseForbidden("end-user not authenticated")

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

# This will provide the CSRF token
def get_csrf(request):
    return HttpResponse(get_token(request))
