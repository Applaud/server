from django.utils.timezone import utc
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext, Template, Context
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
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
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile, RatedDimension
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
        return HttpResponseRedirect(reverse("home"))

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

# Adding employees. Can handle a comma-separated field of emails (like
# textarea/textfield) or a CSV file
@business_view
@csrf_protect
def add_employee(request):
    profile = request.user.businessprofile
    if request.method == "POST":
        # Get emails from POST
        emails = request.POST['emails']
        email_list=strip_and_validate_emails(emails)
        
        # If they choose to upload a CSV file.
        if request.FILES:
            user = profile.user.username
            with open('/tmp/%s.txt'%user, 'w+') as destination:
                for chunk in request.FILES['csv'].chunks():
                    destination.write(chunk)

                # Union of POST emails and CSV emails
                email_list.extend( strip_and_validate_emails(destination.read()) )

        # Render the contents of the email
        _add_employee(set(email_list),
                      request.user.businessprofile.business_name,
                      request.user.businessprofile.goog_id)

        # Success message
        messages.add_message(request, messages.SUCCESS, "Emails have been sent inviting your employees to join Apatapa. Thank you!")

        return HttpResponseRedirect(reverse('business_home'))

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
    except EmployeeProfile.DoesNotExist:
        return False

@business_view
@csrf_protect
def manage_ratingprofiles(request):
    '''
    {'profile_id':#,
     'insert':"asdfasdfasdf",
     'remove':--,
     'remove_dim':dimid,

     'replace_dim':dimid,
     'with_dim':"newtext"

     'deactivate_dim':dimid,
     'activate_dim':dimid
     '''
    if len(set(['insert','remove','replace_dim','remove_dim','deactivate_dim', 'activate_dim'])
           & set(request.POST.keys()))==0:
        return HttpResponse(json.dumps({'error':"No valid JSON dictionary key sent to this view."}))

    try:
        rating_profile = RatingProfile.objects.get(id=int(request.POST['profile_id']))
    except RatingProfile.DoesNotExist:
        return HttpResponse(json.dumps({'error':"Rating profile did not exist."}))

    # Insert one dimension
    if 'insert' in request.POST:
        dim = RatedDimension(title=request.POST['insert'],
                             rating_profile=rating_profile)
        dim.save()

    # Delete the rating profile and all associated data. Warn the user
    # before doing this!
    if 'remove' in request.POST:
        alldims = rating_profile.rateddimension_set.all()
        for dim in alldims:
            dim.rating_set.all().delete()
        alldims.delete()
        rating_profile.delete()

    # Remove one dimension
    if 'remove_dim' in request.POST:
        dim = RatedDimension.objects.get(id=int(request.POST['remove_dim']))
        dim.delete()

    if 'replace_dim' in request.POST:
        # Step 1: Change the title in all the ratings for this dimension
        dim = RatedDimension.objects.get(id=int(request.POST['replace_dim']))
        for rating in dim.rating_set.all():
            rating.title = request.POST['with_dim']
            rating.save()

        # Step 2: Change the ratingprofile itself
        dim.title = request.POST['with_dim']
        dim.save()

    if 'deactivate_dim' in request.POST:
        dim = RatedDimension.objects.get(id=int(request.POST['deactivate_dim']))
        dim.is_active = False
        dim.save()

    if 'activate_dim' in request.POST:
        dim = RatedDimension.objects.get(id=int(request.POST['activate_dim']))
        dim.is_active = True
        dim.save()

        
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

    rp = RatingProfile(title=request.POST['title'],
                       business=profile)
    rp.save()

    while 'dim%d'%i in request.POST:
        dim = RatedDimension(title=request.POST['dim%d'%i],
                             rating_profile=rp)
        i += 1

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

            messages.add_message(request, messages.SUCCESS, "Your survey has been saved.")
            return HttpResponse("") # Empty response = all went well
        # We're getting data for this business' survey.
        else:
            return HttpResponse(json.dumps({'survey':survey},
                                           cls=SurveyEncoder),
                                mimetype='application/json')

# A function to recieve a comma-separated email list, strip them
# and check them for validity
def strip_and_validate_emails(emails):
    email_list = [i.strip(' ') for i in emails.split(',')]
    email_list=filter(lambda a: re.match(r"[^@]+@[^@]+\.[^@]+", a), email_list)
    return email_list

@business_view
def business_welcome(request):
    ''' View that is called only the first time that a business logged in
    '''
    profile = request.user.businessprofile
    if request.method != "POST":
        return render_to_response('business_welcome.html',
                                  {'business':profile},
                                  context_instance=RequestContext(request))
    if request.method == "POST":
        return add_employee(request)
    
@business_view
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

        # Make sure we have a dictionary entry for each dimension
        for dimension in employee.rating_profile.rateddimension_set.all(): 
            ratings[dimension.title] = [d.rating_value for d in dimension.rating_set.filter(employee=employee)]

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
    print "Seeing something"
    
    if request.method == 'GET' or request.method=='POST':
        data = json.loads(request.POST['data'])

        print "Employee ids: "+str(data['employee_ids'])
        print "Rating categories: "+str(data['rating_categories'])

        # If more than one category
        # include type(data['rating_categories'])
        if len(data['employee_ids'])==0:
            employee_ids = [ employee.id for employee in profile.employeeprofile_set.all() ]
        else:
            employee_ids = data['employee_ids']
        
        category_list = data['rating_categories']
        
        if len(data['rating_categories']) > 0:
            first_row=["category"]
            for category in data['rating_categories']:
                dimension = models.RatedDimension.objects.get(pk=category)
                first_row.append(dimension.title)
                
            chart_data = [first_row]
            for employee in employee_ids:
                chart_data.append(_get_average_employee_analytics(employee, category_list))
        else:
        # If only one category
            category = data['rating_categories'][0]
            first_row=["rating","poor","fair","good","excellent","glorious"]
            chart_data = [first_row]
            for employee in employee_ids:
                chart_data.append(_get_employee_analytics(employee,category))

        to_chart = _make_google_charts_data(chart_data)
        print "About to print array"
        print to_chart
        return HttpResponse(json.dumps(to_chart),
                            mimetype="application/json")

def _get_average_employee_analytics(employee_id, category_ids):
    """A function to return average statistics of an employee
       employee_id is employee_id
       category_ids is a list of RatedDimension ids
       if rating_titles is empty it will use all RatedDimension titles
       returns: [first_name_last_name, avg_rating_1, avg_rating_2]
    """
    try:
        employee = models.EmployeeProfile.objects.get(pk=employee_id)
    except EmployeeProfile.DoesNotExist:
        return False
    
    ret=[]
    ret.append("%s %s"%(employee.user.first_name, employee.user.last_name))
    
    ratings = []
    profile = employee.rating_profile
 
    if len(category_ids) == 0 or not category_ids:
        category_ids = [rating.id for rating in employee.rating_profile.rateddimension_set.all()]
   
    for category in category_ids:
         dimension = models.RatedDimension.objects.get(pk=category)
         rel_ratings = [rating.rating_value for rating in dimension.rating_set.filter(employee=employee)]
         ratings.append(average(rel_ratings))
         
    ret.extend(ratings)
    return ret              

def _get_employee_analytics(employee_id, category):
    """A function to return the number of ratings (1-5) of an employee for a single category
       employee_id is employee_id
       category is the RatedDimension id to use
       returns: [first_name_last_name, num_ratings_1, num_ratings_2]
    """
    try:
        employee = models.EmployeeProfile.objects.get(pk=employee_id)
    except EmployeeProfile.DoesNotExist:
        return False
    
    ret = []
    quantity_of_ratings = [ 0 for i in range(5)]
    ret.append("%s %s"%(employee.user.first_name, employee.user.last_name))
    
    profile = employee.rating_profile
    dimension = models.RatedDimension.objects.get(pk=category)
    ratings = dimension.rating_set.filter(employee=employee)

    for rating in ratings:
        quantity_of_ratings[rating.rating_value]+=1
    
    str_list_of_ratings = [quantity_of_ratings[i] for i in range(len(quantity_of_ratings))]
    ret.extend(quantity_of_ratings)
    return ret


def _make_google_charts_data(data):
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
	except NewsFeedItem.DoesNotExist:
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
    if not nums:
        return 0
    else:
        return (float(sum(nums))/len(nums))
