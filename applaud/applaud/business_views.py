from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile
from django.template import RequestContext, Template, Context
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from datetime import datetime
from django.contrib.auth.models import Group, User
# TODO: clean up the next 3
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files import File
from django.core.mail import send_mail, BadHeaderError
import sys
import json
import urllib2
from applaud import forms
from applaud import models
from registration import forms as registration_forms
from views import SurveyEncoder, EmployeeEncoder
import re
import csv

# Employee stuff.


# Adding employees. A lot of the code (minus the CSV input) is used from the business welcome view
@csrf_protect
def add_employee(request):
    if request.user.is_authenticated():
        try:
            profile=request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseRedirect("/")
    if request.method == "POST":
        # Get emails from POST
        emails = strip_and_validate_emails(request.POST['emails'])
        success=_add_employee(emails,
                              request.user.businessprofile.business_name,
                              request.user.businessprofile.goog_id)
    if success:
        # return HttpResponse(json.dumps({'message':'Great Success!'}),
        #                     context_instance=RequestContext(request))
        return HttpResponse("All went well!")
    else:
        # return HttpResponse(json.dumps({'message':'Employee could not be added. Please check the email again'}),
        #                      context_instance=RequestContext(request))
        return HttpResponse("Something went wrong.")

def _add_employee(emails, biz_name, biz_goog_id):
    sys.stderr.write("%s, %s, %s"%(str(emails), biz_name, biz_goog_id))
    email_template=Template('email_employee.txt')
    context = {'business':biz_name,
               'goog_id':biz_goog_id}
    message = render_to_string('email_employee.txt',
                               context)
    subject = 'Register at apatapa.com!'
    from_email='register@apatapa.com'

    try:
        send_mail(subject, message, from_email, emails)
        return True
    except BadHeaderError:
        return False

# View function that lists employees for employees.html
def manage_employees(request):
    if request.user.is_authenticated():
        profile=""
        #Are we a business?
        try:
            profile=request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseRedirect("/")
        return render_to_response('employees.html',
                                  {'list':_list_employees(profile.id),
                                   'rating_profiles':_list_rating_profiles(profile.id)},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/accounts/login")


# List the employees for a business
def _list_employees(businessID):
    business_profile = BusinessProfile.objects.get(id=businessID)
    employee_list = EmployeeProfile.objects.filter(business=business_profile)

    return employee_list

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

        # Exchanges information (employee <--> POST data)
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

# List the rating profiles for a business
def _list_rating_profiles(businessID):
    rps = BusinessProfile.objects.get(id=businessID)
    return [{'title':rp.title,'dimensions':rp.dimensions} for rp in rps.ratingprofile_set.all()]
    
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
        
# A function to recieve a comma-separated email list, strip them
# and check them for validity
def strip_and_validate_emails(emails):
    email_list = [i.strip(' ') for i in emails.split(',')]
    email_list=filter(lambda a: re.match(r"[^@]+@[^@]+\.[^@]+", a), email_list)
    return email_list

''' View that is called only the first time that a business logged in
'''
def business_welcome(request):
    if request.user.is_authenticated():
	# Are we a business?
	try:
	    profile = request.user.businessprofile
	except BusinessProfile.DoesNotExist:
	    # Authernticated but not a business
            return HttpResponseRedirect('/accounts/login')
        
    else:
        return HttpResponseRedirect('/accounts/login')  
    
    if request.method != "POST":
        return render_to_response('business_welcome.html',
                                  {'business':profile},
                                  context_instance=RequestContext(request))
    # Business is authenticated
    if request.method == "POST":
        # Get emails from POST
        emails = request.POST['emails']
        email_list=strip_and_validate_emails(emails)
        email_template=Template('email_employee.txt')
        
        # If they choose to upload a CSV file.
        if request.FILES:
            user = profile.user.username
            r = open('/tmp/%s.txt'%user, 'w+')
            reader = File(r)
            emp_list=''
            reader_str=''
            with reader as destination:
                for chunk in request.FILES['csv'].chunks():
                    destination.write(chunk)
                    reader_str+=chunk

                row_list = []
                for i in reader_str.split(','):
                    row_list.append(str(i)+' ')                

                count = 0
                for row in reader:
                    emp_list += row_list[(32*count)+28]+', '
                    sys.stderr.write(row_list[(32*count)+28])
                    count+=1
            emp_list_final = strip_and_validate_emails(emp_list)
            email_list.extend(emp_list_final)


        success=_add_employee(email_list,
                              request.user.businessprofile.business_name,
                              request.user.businessprofile.goog_id)
                                
        if not success:
            return HttpResponse('Invalid header found')
        return HttpResponseRedirect('/business/')
    
def business_home(request):
    return render_to_response('business.html')


# Checking analytics.
def analytics(request):
    if request.user.is_authenticated():
        try:
            profile = request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return render_to_response('fail.html',
                                      {'debug': "You're no business!"},
                                      context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')

    # For each employee, get all their ratings and gather them into a dictionary.
    employees = []
    for employee in list(profile.employeeprofile_set.all()):
        employee_dict = {}
        ratings = {}
        employee_dict['name'] = '%s %s' % (employee.user.first_name, employee.user.last_name)
        for dimension in employee.rating_profile.dimensions: # Make sure we have a dictionary entry for each dimension
            ratings[dimension] = []
        for rating in list(employee.rating_set.all()): # Make a list of all the ratings for each dimension
            ratings[rating.title].append(rating.rating_value)

        # Calculate the average of that list or each dimension
        for rating in ratings.keys():
            ratings[rating] = 'N/A' if len(ratings[rating]) == 0 else sum(ratings[rating])/len(ratings[rating])
        print ratings
        employee_dict['ratings'] = ratings
        employees.append(employee_dict)

    # Get all the surveys for this business.
    survey_dict = {}
    if len(profile.survey_set.all()) > 0:
        survey = profile.survey_set.all()[0] # Just in case we've got more than one
        survey_dict = {'title': survey.title,
                       'description': survey.description,
                       'questions': []}
        # Gather all the question responses in a dict.
        for question in list(survey.question_set.all()):
            question_dict = {'label': question.label,
                             'responses': []}
            for response in question.questionresponse_set.all():
                question_dict['responses'].append(response.response)
            survey_dict['questions'].append(question_dict)

    # Get all the general feedback.
    feedback = models.GeneralFeedback.objects.filter(business=profile)
    return render_to_response('business_analytics.html',
                              {'employees': employees,
                               'survey': survey_dict,
                               'feedback': feedback,
                               'business': profile.user.businessprofile},
                              context_instance=RequestContext(request))
