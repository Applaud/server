from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from applaud.models import RatingProfile
from django.template import RequestContext, Template
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from datetime import datetime
import sys
import json
import urllib2
from applaud import forms
from applaud import models

def index(request):
	username = ""
	if request.user.is_authenticated():
		username = request.user.username
	return render_to_response('index.html',{'username':username})

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
			 "longitude":-83.004617},
			{"name":"Seymour House of Smiles",
			 "type":"Orthodontist",
			 "goog_id":"27ea39c8fed1c0437069066b8dccf958a2d06f19",
			 "latitude":39.981934,
			 "longitude":-83.004676},
			],
		}
	return HttpResponse(json.dumps(res))

def checkin(request):
	if not "latitude" in request.GET or not  "longitude" in request.GET:
	    error = "Latitude & longitude confusion...."
	    return render_to_response('error.html',{"error":error})   

	lat = request.GET["latitude"]
	lon = request.GET["longitude"]	

	goog_api_key="AIzaSyCbw9_6Mokk_mKwnH02OYyB6t5MrepFV_E"
	radius="100"

	from_goog = urllib2.urlopen("https://maps.googleapis.com/maps/api/place/search/json?location="+lat+","+lon+"&radius="+radius+"&sensor=false&key="+goog_api_key)

	to_parse = json.loads(from_goog.read())
	#return HttpResponse(to_parse)

	ret = {"nearby_businesses":[],}

	for entry in to_parse["results"]:
		new_biz={"name":entry["name"],
			 "type":entry["types"][0],
			 "goog_id":entry["id"],
			 "latitude":entry["geometry"]["location"]["lat"],
			 "longitude":entry["geometry"]["location"]["lng"]}
		ret["nearby_businesses"].append(new_biz)
	ret = json.dumps(ret)
	return HttpResponse(ret)

# This allows a user to save and view newsfeed posts
@csrf_protect
def newsfeed_create(request):
	if request.method == 'POST':
	    n = forms.NewsFeedItemForm(request.POST)
	    newsitem = n.save(commit=False)
	    newsitem.date = datetime.now()
	    newsitem.save()
	    
	f = forms.NewsFeedItemForm()
	newsfeed = models.NewsFeedItem.objects.all()
	
	return render_to_response('basic_newsfeed.html',
				  {'form':f, 'list':newsfeed},
				  context_instance=RequestContext(request))

# Delete a newsfeed item
@csrf_protect
def delete_newsfeed_item(request):
	return HttpResponse("Implement this view!")

#Serves the newsfeed to iOS	
def nfdata(request):
	# TODO: access newsfeed for a particular business
	# 
	# if ( request.GET ):
	# 	business_id = request.GET['business_id']

	nfitems = models.NewsFeedItem.objects.all()
	nfitem_list = []
	for nfitem in nfitems :
		nfitem_list.append({'title':nfitem.title,
				    'subtitle':nfitem.subtitle,
				    'body':nfitem.body,
				    'date':nfitem.date.strftime('%Y-%m-%d %I:%M')})

	ret = { 'newsfeed_items':nfitem_list }

	return HttpResponse(json.dumps(ret))

@csrf_protect
def edit_newsfeed_item(request):
        if request.method == 'POST':
                n = forms.NewsFeedItemForm(request.POST)
	        newsitem = n.save(commit=False)
       	        newsitem.date = datetime.now()
       	        newsitem.save()
	    	        	
	else:
		try:
			n = NewsFeedItem.objects.get(id=request.GET['id'])
		except:
        		return render_to_response('fail', {}, context_instance=RequestContext(request))
						  
                dict = dict((key, value) for key, value in n.__dict__.iteritems() 
			    if not callable(value) and not key.startswith('__'))
		
                f = forms.NewsFeedItemForm(initial=dict)
        	newsfeed = models.NewsFeedItem.objects.all()
       	
                return render_to_response('basic_newsfeed.html',
				  {'form':f, 'list':newsfeed},
				  context_instance=RequestContext(request))

@csrf_protect
def create_employee(request):
	if  request.method == 'POST':
		employee_form = forms.EmployeeForm(request.POST)
		employee_form.save()

	new_form = forms.EmployeeForm()
	employees = models.Employee.objects.all()

	return render_to_response('employees.html',
				  {'form':new_form, 'list':employees},
				  context_instance=RequestContext(request))

def rate_employee(request):
	# if not 'employee' in request.GET or not 'ratings' in request.GET:
	#     error = "Must supply employee and ratings to rate an employee."
	#     return render_to_response('error.html',{"error":error})   
	
	# employee = request.GET['employee']
	# ratings = request.GET['ratings']
	return HttpResponse("Coming soon!")

class EmployeeEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, models.Employee):
			dimensions = o.rating_profile.dimensions
			res = {'first_name':o.first_name,
			       'last_name':o.last_name,
			       'bio':o.bio,
			       'ratings':
				       {'rating_title':o.rating_profile.title,
					'dimensions':dimensions}
			       }
			return res
		else:
			return json.JSONEncoder.default(self, o)

def employee_list(request):
	'''List the employees by last name and first name.
	Also give the definition of the rating profile with which they are associated.
	'''
	return HttpResponse(json.dumps(list(models.Employee.objects.all()),
				       cls=EmployeeEncoder),
			    mimetype='application/json')

@csrf_protect
def create_rating_profile(request):
    '''Create a rating profile.
    Takes a variable number of text fields and turns them into dimensions
    for a rating profile. Also includes the title.
    '''
    # if not request.user.is_authenticated():
    #     return HttpResponseRedirect('/login')
    if request.method == 'GET':
        return render_to_response('employeeprofile_create.html',
                                  {},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
	sys.stderr.write(str(request.POST))
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
            return render_to_response('create_rating_profile.html',
                                      errors,
                                      context_instance=RequestContext(request))
        rp = RatingProfile(title=title, dimensions=dimensions)
        rp.save()
	
        return HttpResponseRedirect('/ratingprofiles')

@csrf_protect
def list_rating_profiles(request):
	l = list(RatingProfile.objects.all())
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
    # if not request.user.is_authenticated():
    #     return HttpResponseRedirect('/login')
    if request.method == 'GET':
        return render_to_response('survey_create.html',
                                  {},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
	sys.stderr.write(str(request.POST))
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

	# First, create the Survey
	s = models.Survey(title=title, description=description)
	s.save()

	# Create each of the questions on the Survey
	for question in questions:
		q = models.Question(label=question['title'],
				    type=question['type'],
				    options= question['options'],
				    survey=s)
		q.save()

        return HttpResponseRedirect('/survey_create')	

def get_survey(request):
    '''Gets the survey for a particular business.
    TODO: get the business ID, and return the right survey for it.
    '''

    # For testing, just get the first survey
    survey = models.Survey.objects.get(id=1)

    # All of the questions associated with the survey
    questions = survey.question_set.all()

    # Making a python object from the query set of questions
    questionList = []
    for question in questions:
	questionList.append({'label':question.label,
			     'type':question.type,
			     'options':question.options})
	
    # Creating a python object from the survey model + questions
    surveyDict = {'title':survey.title,
		  'description':survey.description,
		  'questions':questionList}

    # Returning that as JSON
    return HttpResponse(json.dumps(surveyDict))
    
def register_business(request):
    if request.method == 'POST':
	registrationForm = UserCreationForm(request.POST)
	if registrationForm.is_valid():
	    registrationForm.save()
	    return HttpResponseRedirect('/register_success/')
	else:
	    return HttpResponseRedirect('/register_fail/')

    else:
	form = UserCreationForm()
	return render_to_response('register.html',{'form':form})
    
@csrf_protect
def failed_registration(request):
    return render_to_response('fail.html',
			      {},
			      context_instance=RequestContext(request))

@csrf_protect
def general_feedback(request):
	if request.method != 'POST':
		return HttpResponse(get_token(request))
	feedback = models.GeneralFeedback(feedback=json.load(request)['answer'])
	feedback.save()
	return HttpResponse('foo')

@csrf_protect
def evaluate(request):
	if request.method != 'POST':
		return HttpResponse(get_token(request))
	rating_data = json.load(request)
	if 'employee' in request.POST:
		try:
			e = Employee.objects.get(rating_data['employee']['id'])
		except:
			pass
		for key, value in rating_data['ratings']:
			r = Rating(title=key, rating_value=float(value),employee=e)
			r.save()
	return HttpResponse('foo')

@csrf_protect
def survey_respond(request):
	if request.method != 'POST':
		return HttpResponse(get_token(request))
	for answer in json.load(request)['answers']:
		question = models.Question.objects.get(label=answer['label'])
		response = answer['response']
		qr = models.QuestionResponse(question=question, response=response)
		qr.save()
	return HttpResponse('foo')

# This will provide the CSRF token
def get_csrf(request):
	return HttpResponse(get_token(request))
