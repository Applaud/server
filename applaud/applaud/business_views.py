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
from views import SurveyEncoder, EmployeeEncoder

# Employee stuff.

@csrf_protect
def edit_employee(request):
    if request.user.is_authenticated():
    #Are we a business?
        try:
            profile=request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseRedirect("/")

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

@csrf_protect
def delete_employee(request):
    if request.user.is_authenticated():
        #Are we a business?
        try:
            profile=request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseRedirect("/")

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
        emp = models.EmployeeProfile.objects.get(pk=request.GET['id'])
        return render_to_response('delete_employee_confirmation.html',
                                  {'employee':emp, 'id':request.GET['id']},
                                  context_instance=RequestContext(request))

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
# Survey stuff.
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

        return HttpResponseRedirect('/survey_create')	

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
def create_rating_profile(request):
    '''Create a rating profile.
    Takes a variable number of text fields and turns them into dimensions
    for a rating profile. Also includes the title.
    '''
    if request.method == 'GET':
        # Be sure we're logged in and that we're a business.
        if request.user.is_authenticated() and 'businessprofile' in dir(request.user):
            return render_to_response('create_rating_profile.html',
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
            return render_to_response('fail.html')
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
        rp = RatingProfile(title=title, dimensions=dimensions, business=profile)
        rp.save()
	
        return HttpResponseRedirect('/ratingprofiles')

# Creating/editing newsfeed, looking at the newsfeed.
@csrf_protect
def newsfeed_create(request):
    #What happens if an employee or end-user visits this page?
    if request.user.is_authenticated():
	# Are we a business?
	try:
	    profile = request.user.businessprofile
	except BusinessProfile.DoesNotExist:
	    return HttpResponseRedirect('/fail/')

	username = request.user.username

    else:
        return HttpResponseRedirect('/accounts/business/')

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
            return HttpResponseRedirect("/fail/")

        username=request.user.username
    else:
        return HttpResponseRedirect("/")

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