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
from django.core.urlresolvers import reverse
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
        return HttpResponseRedirect(reverse("auth_login"))

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
@business_view
@csrf_protect
def add_employee(request):
    if request.method == "POST":
        # Get emails from POST
        emails = strip_and_validate_emails(request.POST['emails'])
        success=_add_employee(emails,
                              request.user.businessprofile.business_name,
                              request.user.businessprofile.goog_id)
    if success:
        return HttpResponse("All went well!")
    else:
        return HttpResponse("Something went wrong.")

def _add_employee(emails, biz_name, biz_goog_id):
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
@business_view
def manage_employees(request):
    profile = request.user.businessprofile
    return render_to_response('employees.html',
                              {'employee_list':_list_employees(profile.id),
                               'rating_profiles':_list_rating_profiles(profile.id)},
                                  context_instance=RequestContext(request))

# List the employees for a business
def _list_employees(businessID):
    business_profile = BusinessProfile.objects.get(id=businessID)
    employee_list = list(EmployeeProfile.objects.filter(business=business_profile))

    return employee_list

@business_view
@csrf_protect
def delete_employee(request):
    profile = request.user.businessprofile
    if 'employee_id' in request.POST:
        _delete_employee(request.POST['employee_id'])
        return HttpResponse(json.dumps({'employee_list':_list_employees(profile.id)},
                                       cls=EmployeeEncoder),
                            mimetype='application/json')
    return HttpResponseRedirect(reverse("business_manage_employees"))

# Fully deletes an employeeprofile (including the employee user) from the database
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
    if len(set(['insert','remove','replace_dim','remove_dim','deactivate_dim'])
           & set(request.POST.keys()))==0:
        return HttpResponse(json.dumps({'error':"No valid JSON dictionary key sent to this view."}))

    try:
        rating_profile = RatingProfile.objects.get(id=int(request.POST['profile_id']))
    except RatingProfile.DoesNotExist:
        return HttpResponse(json.dumps({'error':"Rating profile did not exist."}))

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
        
    return HttpResponse(json.dumps({'rating_profiles':_list_rating_profiles(request.user.businessprofile.id)},
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

    profile = request.user.businessprofile
    if request.method != 'POST':
        return HttpResponseRedirect(reverse("business_manage_employees"))

    dimensions = []
    i = 0

    while 'dim%d'%i in request.POST:
        dimensions.append( request.POST['dim%d'%i] )
        i += 1

    rp = RatingProfile(title=request.POST['title'],
                       dimensions=dimensions,
                       business=profile)
    rp.save()

    return HttpResponse(json.dumps({'rating_profiles':
                                        _list_rating_profiles(profile.id)},
                                   cls=RatingProfileEncoder),
                        mimetype='application/json')

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
    # Return the survey page.
    if request.method == 'GET':
        return render_to_response('manage_survey.html',
                                  {'survey_id': survey.id},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        # If we're POSTing survey data.
        if 'survey_id' in request.POST:
            survey.title = request.POST['survey_title']
            survey.description = request.POST['survey_description']
            for question in json.loads(request.POST['questions']):
                # If it's a new question.
                if int(question['question_id']) == 0:
                    q = models.Question(survey=survey)
                else:
                    q = models.Question.objects.get(id=question['question_id'])
                q.label = question['question_label']
                q.options = question['question_options']
                q.type = question['question_type']

                # Set whether this question is visible to users or not.
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
        # We're getting data for this business' survey.
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
        return render_to_response('create_rating_profile.html',
                                  {},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
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
	
        return HttpResponseRedirect(reverse("business_manage_ratingprofiles"))

        
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
            emp_list=''
            reader_str=''
            with open('/tmp/%s.txt'%user, 'w+') as destination:
                for chunk in request.FILES['csv'].chunks():
                    destination.write(chunk)
                email_list.extend( strip_and_validate_emails(destination.read()) )

        # Render the contents of the email
        context = {'business':request.user.username,
                   'goog_id':request.user.businessprofile.goog_id}
        message = render_to_string('email_employee.txt',
                                   context)

        subject = 'Register at apatapa.com!'
        from_email='register@apatapa.com'

        _add_employee(set(email_list),
                      request.user.businessprofile.business_name,
                      request.user.businessprofile.goog_id)
                                
        request.user.businessprofile.first_time = False
        return HttpResponseRedirect(reverse('business_home'))
    
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
@csrf_protect
@business_view
def business_analytics(request):
    """To display various statistics for a business
    """
    profile = request.user.businessprofile
    return render_to_response('business_analytics_test.html',
                              {'business':profile},
                              context_instance=RequestContext(request))
@csrf_protect
@business_view
def get_analytics(request):
    """A view to retrieve statistics for employees, surveys, and general feedback.
       Currently only implemented for employee statistics. Should receive a dictionary of the form:
       {'employee_ids':[%d, %d, %d, ....],
        'rating_categories': }
    """
    profile = request.user.businessprofile
    
    data = json.loads(request.POST['data'])

    if request.method == 'GET' or request.method=='POST':
        first_row=["category"]
        category_list = [category for category in data['rating_categories']]
        first_row.extend(category_list)
        chart_data = [first_row]
        print chart_data
        for employee in data['employee_ids']:
            chart_data.append(_get_average_employee_analytics(employee, category_list))
        
        print chart_data
        # return HttpResponse(json.dumps({'hello':"Hellllloooooooo"}),
        #                    mimetype="application/json")
       
        return HttpResponse(json.dumps(_make_google_charts_data_with_many_categories(chart_data)),
                            mimetype="application/json")
                  
def _make_google_charts_data_with_many_categories(data):
    """A function to make google charts data. The data variable should be of the form
    goog_data=[["category","smelliness",....],[employee_name, data_for_smelliness,...],...,]
    """
    success_chart=[[] for i in range(len(data))]
    print success_chart
    for i in range(len(data)):
        next_list = data[i]
        for j in range(len(next_list)):
            success_chart[i].append(next_list[j])
    
    return success_chart

def _get_average_employee_analytics(employee_id, rating_titles):
    """A function to return average statistics of an employee
       employee_id is employee_id
       rating_titles is a list of rating_titles
       returns: [first_name_last_name, avg_rating_1, avg_rating_2]
    """
    try:
        employee = models.EmployeeProfile.objects.get(pk=employee_id)
    except EmployeeProfile.DoesNotExist:
        return False
    
    ret=[]
    ret.append("%s %s"%(employee.user.first_name, employee.user.last_name))
    
    ratings = {}
    profile = employee.rating_profile

    # First make a dictionary so as not to lose individual ratings
    for rating in employee.rating_set.all():
        #rating has already been accounted for
        if rating.title in ratings:
            ratings[rating.title].append(rating.rating_value)
        else:
            ratings[rating.title]=[rating.rating_value]
     
    
    rating_list=[]
    for title in rating_titles:
        rating_list.append(average(ratings[title]))

    ret.extend(rating_list)
    return ret


def _get_rating_profile(employee_id):
    """Returns a json-able rating_profile object of the form
       rating_profile={'title':%s,
                       'ratings':{'title':['rating_value':%s (TODO: implement %d accross the board)
                                  }}
                      }
    """
    try:
        employee = models.EmployeeProfile.objects.get(pk=employee_id)
    except EmployeeProfile.DoesNotExist:
        return False

    rating_profile = {}
    profile=employee.rating_profile
    rating_profile['title']=profile.title
    ratings={}

    # loop over ratings
    for rating in employee.rating_set.all():
        #rating has already been accounted for
        if rating.title in ratings:
            ratings[rating.title].append(rating.rating_value)
        else:
            ratings[rating.title]=[rating.rating_value]
            

        rating_profile['ratings']=ratings
    return rating_profile
    

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
        
        return HttpResponseRedirect(reverse('business_manage_newsfeed'))
    
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

def average(nums):
    return (float(sum(nums))/len(nums))
