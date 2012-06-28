from django.utils.timezone import utc
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext, Template, Context
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from datetime import datetime
from django.contrib.auth.models import Group, User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files import File
from django.core.mail import send_mail, BadHeaderError
import sys
import json
import urllib2
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile
from applaud import forms, models
from registration import forms as registration_forms
from views import SurveyEncoder, EmployeeEncoder, RatingProfileEncoder, QuestionEncoder
import re
import csv


# 'business_view' decorator.
def business_view(view):
    '''
    Checks a BusinessView to make sure that a user is logged in and
    is in fact a business (i.e., has a BusinessProfile) before the
    view is executed. If either of these tests fail, the user is redirected
    to the appropriate page.
    '''
    def goto_login(*args, **kw):
        return HttpResponseRedirect("/accounts/login/")

    def goto_home(*args, **kw):
        return HttpResponseRedirect("/")

    def wrapper(*args, **kw):
        request = args[0]
        if not request.user.is_authenticated():
            return goto_login(*args, **kw)
        try:
            profile = request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return goto_home(*args, **kw)

        return view(*args, **kw)
            
    return wrapper

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
                                  {'employee_list':_list_employees(profile.id),
                                   'rating_profiles':_list_rating_profiles(profile.id)},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/accounts/login")


# List the employees for a business
def _list_employees(businessID):
    business_profile = BusinessProfile.objects.get(id=businessID)
    employee_list = list(EmployeeProfile.objects.filter(business=business_profile))

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

# @csrf_protect
# def delete_employee(request):
#     if request.user.is_authenticated():
#         #Are we a business?
#         try:
#             profile=request.user.businessprofile
#         except BusinessProfile.DoesNotExist:
#             return HttpResponseRedirect("/")

#         username=request.user.username
#     else:
#         return HttpResponseRedirect("/accounts/login/")

#     if request.method == 'POST':
#         emp = models.Employee.objects.get(pk=request.POST['id'])
#         emp.delete()
        
#         new_form = forms.EmployeeForm()
#         employees = profile.employee_set.all()

#         return render_to_response('employees.html',
#                                   {'form': new_form, 'list': employees},
#                                   context_instance=RequestContext(request))
#     else:
#         emp = models.EmployeeProfile.objects.get(pk=request.GET['id'])
#         return render_to_response('delete_employee_confirmation.html',
#                                   {'employee':emp, 'id':request.GET['id']},
#                                   context_instance=RequestContext(request))

@csrf_protect
def delete_employee(request):
    if request.user.is_authenticated():
        profile = ""
        try:
            profile = request.user.businessprofile
        except BusinessProfile.DoesNotExist:
            return HttpResponseRedirect("/")
    else:
        return HttpReponseRedirect("/accounts/login")

    if 'employee_id' in request.POST:
        _delete_employee(request.POST['employee_id'])
        return HttpResponse(json.dumps({'employee_list':_list_employees(profile.id)},
                                       cls=EmployeeEncoder),
                            mimetype='application/json')
    return HttpResponseRedirect("/business/business_manage_employees")
        
# Fully deletes an employee (including employee) from the database
def _delete_employee(employeeID):
    try:
        profile = EmployeeProfile.objects.get(id=employeeID)
        user = profile.user
        profile.delete()
        user.delete()
        return True
    except:
        pass
    return False

@business_view
@csrf_protect
def manage_ratingprofiles(request):
    '''
    {'profile_id':#,
     'insert':"asdfasdfasdf",
     'remove':--,
     'remove_dim':"dimtitle",

     'replace_dim':"oldtext"
     'with_dim':"newtext"

     'deactivate_dim':"dimtitle"
     '''
    if request.method == 'GET':
        print "GET request: %s"%str(request.GET)
    elif request.method == 'POST':
        print "POST request: %s"%str(request.POST)

    if len(set(['insert','remove','replace_dim','remove_dim','deactivate_dim'])
           & set(request.POST.keys()))==0:
        print "No dice!"
        return HttpResponseRedirect("/business/business_manage_employees/")
    
    try:
        rating_profile = RatingProfile.objects.get(id=int(request.POST['profile_id']))
    except RatingProfile.DoesNotExist:
        return HttpResponseRedirect("/business/business_manage_employees/")

    if 'insert' in request.POST:
        rating_profile.dimensions.append(request.POST['insert'])
        rating_profile.save()

    if 'remove' in request.POST:
        # Delete the rating profile and all associated data. Warn the user before doing this!
        rating_profile.rating_set.all().delete()
        rating_profile.delete()

    if 'remove_dim' in request.POST:
        rating_profile.dimensions.remove(request.POST['remove_dim'])
        rating_profile.save()

    if 'replace_dim' in request.POST:
        # Step 1: Change the title in all the ratings for this dimension
        tochange = rating_profile.rating_set.filter(title=request.POST['replace_dim'][0])
        for rating in tochange:
            rating.title = request.POST['replace_dim'][1]
            rating.save()

        # Step 2: Change the ratingprofile itself
        rating_profile.dimensions.remove(request.POST['replace_dim'])
        rating_profile.dimensions.append(request.POST['with_dim'])
        rating_profile.save()

    if 'deactivate_dim' in request.POST:
        rating_profile.dimensions.remove(request.POST['deactivate_dim'])
        rating_profile.save()

    return HttpResponse(json.dumps({'rating_profiles':_list_rating_profiles(profile.id)},
                                   cls=RatingProfileEncoder),
                        mimetype='application/json')

@business_view
def list_rating_profiles(request):
    profile = request.user.businessprofile
    return HttpResponse(json.dumps({'rating_profiles':_list_rating_profiles(profile.id)},
                                   cls=RatingProfileEncoder),
                        mimetype='application/json')

# List the rating profiles for a business
def _list_rating_profiles(businessID):
    rps = BusinessProfile.objects.get(id=businessID)
    return list(rps.ratingprofile_set.all())

@business_view
@csrf_protect
def new_ratingprofile(request):
    '''
    {'title':"thetitle",
     'dim0':"firstdimensiontext",
     'dim1':"seconddimensiontext",
     ...}
    '''
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/acounts/login/")

    profile = ""
    try:
        profile = request.user.businessprofile
    except BusinessProfile.DoesNotExist:
        return HttpResponseRedirect("/")
    if request.method != 'POST':
        return HttpResponseRedirect("/business/business_manage_employees/")

    dimensions = []
    i = 0
    key = 'dim'+str(i)
    while key in request.POST:
        sys.stderr.write("In loop %s"%key)
        dimensions.append( request.POST['dim%d'%i] )
        i += 1
        key = 'dim'+str(i)

    rp = RatingProfile(title=request.POST['title'],
                       dimensions=dimensions,
                       business=profile)
    rp.save()

    return HttpResponse(json.dumps({'rating_profiles':
                                        _list_rating_profiles(profile.id)},
                                   cls=RatingProfileEncoder),
                        mimetype='application/json')
                        
# Survey stuff.
@business_view
@csrf_protect
def create_survey(request):
    '''Create a survey.
    Takes a variable number of text fields and turns them into questions
    for a survey. Also includes the title and description.
    '''
    if request.method == 'GET':
        # Be sure we're logged in and that we're a business.
        # This uses dir(), but it should be 
        return render_to_response('survey_create.html',
                                  {},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        profile = request.user.businessprofile
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

# Landing page for editing and creating surveys.
# This can both create and edit a survey
@business_view
@csrf_protect
def manage_survey(request):
    '''
    {'survey_id':id,
     'survey_title':"title",
     'survey_description':"description",
     'questions':[{'question_id':qid,
                   'label':qlabel,
                   'options':["option1","option2",...],
                   'active':True/False,
                   'type':TA/TF/RG/CG}, { question2 }, ...]
    }
    '''
    profile = request.user.businessprofile
    survey = ""
    # Get the business' survey.
    try:
        survey = profile.survey_set.get(pk=1)
    except models.Survey.DoesNotExist:
        survey = models.Survey(title="",description="",business=profile)
    if request.method == 'GET':
        return render_to_response('manage_survey.html',
                                  {'survey_id': survey.id},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        if 'survey_id' in request.POST:
            survey.title = request.POST['survey_title']
            survey.description = request.POST['survey_description']
            for question in json.loads(request.POST['questions']):
                print 'question : %s ' % question
                if int(question['question_id']) == 0:
                    print 'new question'
                    q = models.Question(survey=survey)
                else:
                    print 'old question'
                    q = models.Question.objects.get(id=question['question_id'])
                q.label = question['question_label']
                q.options = question['question_options']
                q.type = question['question_type']
                print 'is active: %s' % question['question_active']
                if question['question_active'] == 'true':
                    q.active = True
                else:
                    q.active = False
                if question['should_delete'] == 'true' or not q.label:
                    q.delete()
                else:
                    q.save()
            survey.save()
            return HttpResponse('foo')
        else:
            return HttpResponse(json.dumps({'survey':survey},
                                           cls=SurveyEncoder),
                                mimetype='application/json')


@business_view
@csrf_protect
def create_rating_profile(request):
    '''Create a rating profile.
    Takes a variable number of text fields and turns them into dimensions
    for a rating profile. Also includes the title.
    '''
    if request.method == 'GET':
        # Be sure we're logged in and that we're a business.
        profile = request.user.businessprofile
        return render_to_response('create_rating_profile.html',
                                  {},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
	sys.stderr.write(str(request.POST))
        profile = request.user.businessprofile
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

        
# A function to recieve a comma-separated email list, strip them
# and check them for validity
def strip_and_validate_emails(emails):
    email_list = [i.strip(' ') for i in emails.split(',')]
    email_list=filter(lambda a: re.match(r"[^@]+@[^@]+\.[^@]+", a), email_list)
    return email_list

''' View that is called only the first time that a business logged in
'''
@business_view
def business_welcome(request):
    profile = request.user.businessprofile
    if request.method != "POST":
        return render_to_response('business_welcome.html',
                                  {'business':profile},
                                  context_instance=RequestContext(request))

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

        # Render the contents of the email
        context = {'business':request.user.username,
                   'goog_id':request.user.businessprofile.goog_id}
        message = render_to_string('email_employee.txt',
                                   context)

        subject = 'Register at apatapa.com!'
        from_email='register@apatapa.com'

        try:
            send_mail(subject, message, from_email, email_list)
        except BadHeaderError:
            pass

        success=_add_employee(email_list,
                              request.user.businessprofile.business_name,
                              request.user.businessprofile.goog_id)
                                
        if not success:
            return HttpResponse('Invalid header found')
        request.user.businessprofile.first_time = False
        return HttpResponseRedirect('/business/')
    
def business_home(request):
    return render_to_response('business.html')


# Checking analytics.
@business_view
def analytics(request):
    profile = request.user.businessprofile

    # For each employee, get all their ratings and gather them into a dictionary.
    employees = []
    for employee in list(profile.employeeprofile_set.all()):
        employee_dict = {}
        ratings = {}
        employee_dict['name'] = '%s %s' % (employee.user.first_name, employee.user.last_name)
        for dimension in employee.rating_profile.dimensions: # Make sure we have a dictionary entry for each dimension
            ratings[dimension] = []
        for rating in list(employee.rating_profile.rating_set.all()): # Make a list of all the ratings for each dimension
            # N.B.! This only gives the information directly relevant to the current version
            # of the RatingProfile. Old data is still stored from any previous version! We
            # should display this somehow, and give the business the option of removing it
            # (similar to behavior with surveys)
            if rating.title in ratings:
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
                             'responses': [],
                             'active': question.active}
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


################################################
# Everything newsfeed related for the business #
################################################
@csrf_protect
@business_view
def manage_newsfeed(request):
    #This view will check allow a business to create, edit, and delete items from their newsfeed
    profile = request.user.businessprofile

    newsfeed = profile.newsfeeditem_set.all()
    # Business is authenticated
    return render_to_response('manage_newsfeed.html',
                              {'business':profile,
                               'list':newsfeed},
                              context_instance=RequestContext(request))

# Creating/editing newsfeed, looking at the newsfeed.
@csrf_protect
@business_view
def newsfeed_create(request):
    profile = request.user.businessprofile

    if request.method == 'POST':
	n = forms.NewsFeedItemForm(request.POST)
	newsitem = n.save(commit=False)
	newsitem.date = datetime.utcnow().replace(tzinfo=utc)
	newsitem.date_edited = datetime.utcnow().replace(tzinfo=utc)
        newsitem.business = profile
	newsitem.save()
        
        return HttpResponseRedirect('/business/business_manage_newsfeed/')
    
    f = forms.NewsFeedItemForm()
    	
    return render_to_response('create_newsfeed.html',
				  {'form':f},
				  context_instance=RequestContext(request))

@csrf_protect
@business_view
def edit_newsfeed(request):
    profile=request.user.businessprofile

    if request.method == 'POST':	
	n = models.NewsFeedItem.objects.get(pk=request.POST['id'])
	d = {'title':request.POST['title'],
	     'subtitle':request.POST['subtitle'],
	     'body':request.POST['body'],
             'date_edited':datetime.utcnow().replace(tzinfo=utc)}
	
	n.change_parameters(d)
	n = n.save()

	f = forms.NewsFeedItemForm()
	newsfeed = profile.newsfeeditem_set.all()
	return render_to_response('manage_newsfeed.html',
				  {'business':profile, 'form':f, 'list':newsfeed},
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
@business_view
def delete_newsfeed_item(request):
    profile = request.user.businessprofile

    #Request is POST - Business has selected and confirmed news feed item deletion
    if request.method == 'POST':
	n = models.NewsFeedItem.objects.get(pk=request.POST['id'])
	n.delete()
	
        f = forms.NewsFeedItemForm()
        newsfeed = profile.newsfeeditem_set.all()
	
        return render_to_response('manage_newsfeed.html',
				  {'form':f, 'list':newsfeed},
				  context_instance=RequestContext(request))

    #Request is GET - Send to confirmation page
    else:
	n = models.NewsFeedItem.objects.get(pk=request.GET['id'])
	return render_to_response('delete_newsfeed.html',
				  {'item':n, 'id':request.GET['id']},
				  context_instance=RequestContext(request))
