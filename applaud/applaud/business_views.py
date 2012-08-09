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
import views
import re
import csv
import os
import settings
import Image
import StringIO
import hashlib

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
    return render_to_response('manage_employees.html',
                              {'employee_list':_list_employees(profile.id),
                               'rating_profiles':_list_rating_profiles(profile.id)},
                                  context_instance=RequestContext(request))

# List the employees for a business (view)
@business_view
def list_employees(request):
    return HttpResponse(json.dumps({'employee_list':
                                        _list_employees(request.user.businessprofile.id)},
                                   cls=views.EmployeeEncoder),
                        mimetype='application/json')

# List the employees for a business
# Helper function for above
def _list_employees(businessID):
    business_profile = BusinessProfile.objects.get(id=businessID)
    employee_list = list(EmployeeProfile.objects.filter(business=business_profile))

    return employee_list

# A view which takes an employee id through get, checks if the requesting business has the authority
# to view the specific employees stats and returns the data.
# On errors, returns an error message
@business_view
def list_employee(request):
    if request.method == 'GET':
        profile = request.user.businessprofile
        error = ""
        if "employee" in request.GET:
            emp_id = request.GET['employee']
            
            try:
                employee = models.EmployeeProfile.objects.get(pk=emp_id)
                if employee.business == profile:
                    return HttpResponse(json.dumps({'employee':employee},
                                                   cls=EmployeeEncoder),
                                        mimetype='application/json')
                else:
                    error ="You are not authorized to see the statistics of that employee."
                    return HttpResponse({'error':error})

            except EmployeeProfile.DoesNotExist:
                error = "Employee with id "+emp_id+" does not exist"
                return HttpResponse({'error':error})
    else:
        return HttpResponse({'foo':"FOOO!"})


@business_view
@csrf_protect
def delete_employee(request):
    profile = request.user.businessprofile
    if 'employee_id' in request.POST:
        _delete_employee(request.POST['employee_id'])
        return list_employees(request)
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

     'is_text': 'true' | 'false',
     
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
    if 'insert' in request.POST and request.POST['insert']:
        dim = RatedDimension(title=request.POST['insert'],
                             is_text=True if request.POST['is_text'] == 'true' else False,
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

    if 'replace_dim' in request.POST and request.POST['with_dim']:
        # Step 1: Change the title in all the ratings for this dimension
        dim = RatedDimension.objects.get(id=int(request.POST['replace_dim']))
        for rating in dim.rating_set.all():
            rating.title = request.POST['with_dim']
            # Convert to using rating_text, if there wasn't already something there
            if request.POST['is_text'] == 'true' and not rating.rating_text:
                rating.rating_text = str(rating.rating_value)
            rating.save()

        # Step 2: Change the ratingprofile itself
        dim.title = request.POST['with_dim']
        dim.is_text = True if request.POST['is_text'] == 'true' else False
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
                                   cls=views.RatingProfileEncoder),
                        mimetype='application/json')

@business_view
def list_rating_profiles(request):
    profile = request.user.businessprofile
    return HttpResponse(json.dumps({'rating_profiles':_list_rating_profiles(profile.id)},
                                   cls=views.RatingProfileEncoder),
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
    'dimensions':[
     {'dimension' :"firstdimensiontext", 'is_text': boolean},
     {'dimension':"seconddimensiontext", 'is_text': boolean},
    ]
     ...}
    '''

    # Profiles must have titles
    if 'title' not in request.POST:
        return HttpResponse("")
    profile = request.user.businessprofile
    if request.method != 'POST':
        return HttpResponseRedirect(reverse("business_manage_employees"))
    rp = RatingProfile(title=request.POST['title'],
                       business=profile)
    rp.save()
    for dim in json.loads(request.POST['dimensions']):
        dim = RatedDimension(title=dim['dimension'],
                             is_text=dim['is_text'],
                             rating_profile=rp)
        dim.save()
    return HttpResponse(json.dumps({'rating_profiles':_list_rating_profiles(profile.id)},
                                   cls=views.RatingProfileEncoder),
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
        survey = profile.survey_set.all()[0]
    except models.Survey.DoesNotExist:
        survey = models.Survey(title="",description="",business=profile)
    print survey
    if request.method == 'POST':
        print type(json.loads(request.POST['questions']))
        # If we're POSTing survey data.
        if 'survey_id' in request.POST:
            survey.title = request.POST['survey_title']
            survey.description = request.POST['survey_description']
            for question in json.loads(request.POST['questions']):
                print question
                # If it's a new question.
                if int(question['question_id']) == 0:
                    # If this is a new question that should be deleted, just keep on walking.
                    if question['should_delete'] == 'true':
                        continue
                    q = models.Question(survey=survey)
                else:
                    q = models.Question.objects.get(id=question['question_id'])
                q.label = question['label']
                q.options = question['options']
                q.type = question['type']

                # Set whether this question is visible to users or not.
                if question['active'] == 'true':
                    q.active = True
                else:
                    q.active = False
                if question['should_delete'] == 'true' or not q.label:
                    q.delete()
                else:
                    q.save()
            survey.save()

            messages.add_message(request, messages.SUCCESS, "Your survey has been saved.")
#            return HttpResponseRedirect(reverse('business_controlpanel')) # Empty response = all went well
            return HttpResponse('')
        # We're getting data for this business' survey.
    else:
        print survey
        return HttpResponse(json.dumps({'survey':survey},
                                       cls=views.SurveyEncoder),
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

@csrf_protect
@business_view
def business_profile(request):
    profile = request.user.businessprofile
    if request.method == "GET":
        return render_to_response('business_profile.html',
                                  {'business': profile},
                                  context_instance=RequestContext(request))
    # Else it's a POST.
    try:
        profile.primary_color = request.POST['primary_color']
    except ValueError, ValidationError:
        print "value/validation error (primary)"
    try:
        profile.secondary_color = request.POST['secondary_color']
    except ValueError, ValidationError:
        print "value/validation error (secondary)"
    profile.save()
    if 'logo_image' in request.FILES:
        filename = '%s_%s_logo.jpg' % (profile.id,
                                  profile.business_name)
        save_image(profile.logo, filename, request.FILES['logo_image'])
    messages.add_message(request, messages.SUCCESS, 'Profile updated!')
    return HttpResponseRedirect(reverse('business_control_panel'))

@csrf_protect
@business_view
def analytics(request):
    """To display various statistics for a business
    """
    profile = request.user.businessprofile
    return render_to_response('business_analytics.html',
                              {},
                              context_instance=RequestContext(request))

@business_view
def stats(request):
    """A view to retrieve all statistics for employees, and questions associated with a particular business.
       This should be done with a GET request.
    """
    profile = request.user.businessprofile

    if request.method == 'GET':
        business_profile = request.user.businessprofile
        return_data = {}

        for employee in profile.employeeprofile_set.all():
            all_ratings = sorted(list(employee.rating_set.all()),key=lambda e:e.date_created)

            encoded_employee = views.EmployeeEncoder().default(employee)
            encoded_employee['ratings'] = [views.RatingEncoder().default(r) for r in all_ratings]

            if not 'employees' in return_data:
                return_data['employees']=[encoded_employee]
            else:
                return_data['employees'].append(encoded_employee)


        #Assumes a business only has a single survey
        survey = profile.survey_set.all()[0]
        
        for question in survey.question_set.all():
            print "loopin"
            all_ratings = sorted(list(question.questionresponse_set.all()), key=lambda e: e.date_created)
            encoded_question = views.QuestionEncoder().default(question)
            encoded_question['ratings'] = [views.QuestionResponseEncoder().default(r) for r in all_ratings]

            if not 'questions' in return_data:
                return_data['questions']=[encoded_question]
            else:
                return_data['questions'].append(encoded_question)
            
        return HttpResponse(json.dumps({'data':return_data}),
                            mimetype='application/json')
            
    return render_to_response('business_stats.html',
                              {},
                              context_instance=RequestContext(request))

@csrf_protect
@business_view
def get_analytics(request):
    """A view to retrieve statistics for employees, surveys, and general feedback.
       Currently only implemented for employee statistics. Should receive a dictionary of the form:
       {'employee_ids':[%d, %d, %d, ....],
        'rating_categories':[],
        'start': ,
        'stop': }
    """
    profile = request.user.businessprofile
    
    if request.method == 'GET' or request.method=='POST':
        data = json.loads(request.POST['data'])
        category_list = data['rating_categories']
       
        # If no employees are passed in, select all employees
        if len(data['employee_ids'])==0:
            print "employee ids was empty, now setting it to all"
            employee_ids = [ employee.id for employee in profile.employeeprofile_set.all() ]
        else:
        # Otherwise, use exactly the employees passed in    
            employee_ids = data['employee_ids']
        
        # Determining approproate start and stop times
        if data['start']:
            start_time = data['start']
        else:
            start_time = 0

        if data['stop']:
            stop_time = data['stop']
        else:
            stop_time = 0
        
        # Are there multiple rating profiles amongst the selected employees?
        # If there are, only display information on 'Quality'
        if _is_multiple_rating_profiles(employee_ids):
            print "in multiple rating profiles"
            chart_data = _get_only_quality_chart_data(employee_ids, start_time, stop_time)
        
        else:
            if len(category_list)==0:
                an_employee = models.EmployeeProfile.objects.get(id=employee_ids[0])
                # There is only one rating profile, set category_list to all RatedDimensions in it
                category_list = [rating.id for rating in an_employee.rating_profile.rateddimension_set.all()]    

            # category_list has at least one category
            if len(category_list) > 1:
                first_row=["category"]
                for category in category_list:
                    dimension = models.RatedDimension.objects.get(pk=category)
                    first_row.append(dimension.title)
                
                chart_data = [first_row]
                for employee in employee_ids:
                        chart_data.append(_get_average_employee_analytics(employee, category_list))
        
            else:
                # If only one category
                category = category_list[0]
                first_row=["rating","poor","fair","good","excellent","glorious"]
                chart_data = [first_row]
                for employee in employee_ids:
                    chart_data.append(_get_employee_analytics(employee,category))
        
            
        to_chart = _make_google_charts_data(chart_data)
    
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
 
    for category in category_ids:
         dimension = models.RatedDimension.objects.get(pk=category)
         rel_ratings = [rating.rating_value for rating in dimension.rating_set.filter(employee=employee)]
         ratings.append(average(rel_ratings))
         
    ret.extend(ratings)
    return ret              

def _get_employee_analytics(employee_id, category, start_time, stop_time):
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


def average(the_list):
    if len(the_list) == 0:
        return 0
    else:
        return float(sum(the_list))/len(the_list)

#Determines if there is more than one rating profile amongst a set of employees
def _is_multiple_rating_profiles(employee_ids):
    rating_profiles=[]
    for e in employee_ids:
        try:
            employee = models.EmployeeProfile.objects.get(id=e)
            rating_profiles.append(employee.rating_profile)
        except EmployeeProfile.DoesNotExist:
            pass
    if len(set(rating_profiles))==1:
        return False

    return True
        
# A function to assemble chart data for the single dimension quality for a list
# of employees with disjoint rating_profiles
def _get_only_quality_chart_data(employee_ids, start_time, stop_time):
    first_row=["rating","poor","fair","good","excellent","glorious"]
    chart_data = [first_row]
    for employee in employee_ids:
        category = employee.rating_profile.rateddimension_set.filter(title="Quality").id
        chart_data.append(_get_employee_analytics(employee,category, start_time, stop_time))
        
    return chart_data

################################################
# Everything newsfeed related for the business #
################################################
@csrf_protect
@business_view
def add_newsfeeditem(request):
    '''
    This view allows a business to add a single newsfeed item. This view CANNOT BE AJAX'D,
    since we are uploading filey bits (image).
    '''
    
    # Business' profile
    profile = request.user.businessprofile
    nfitem = models.NewsFeedItem(title=request.POST['title'],
                                 subtitle=request.POST['subtitle'],
                                 body=request.POST['body'],
                                 date=datetime.now(),
                                 date_edited=datetime.now(),
                                 business=profile)
    nfitem.save()
    if 'image' in request.FILES:
        try:
            filename = '%s_%s_%s.jpg' % (profile.id,
                                         profile.business_name,
                                         feed.title[:10])
            save_image(feed.image, filename, request.FILES['image' % i])
        except IOError:
            pass

    nfitem.save()
    return HttpResponse("")
    
    
@csrf_protect
@business_view
def manage_newsfeed(request):
    '''
    This view will check allow a business to edit and delete
    items from their newsfeed.

    Format of JSON in POST requests:

    {'delete_newsfeed':'true' # if deleting a newsfeed,
     'id':newfeed_id }
    '''

    profile = request.user.businessprofile
    if request.method == 'GET':
        newsfeed = profile.newsfeeditem_set.all()
        # Business is authenticated
        return render_to_response('business_control_panel.html',
                                  {'business':profile,
                                   'feeds':newsfeed},
                                  context_instance=RequestContext(request))


    # Otherwise, it's a POST.
    print str(request.POST)
    profile = request.user.businessprofile

    # Delete a newsfeed
    if 'delete_newsfeed' in request.POST:
        print "Deleting something"
        try:
            print "About to try deleting id %d"%int(request.POST['id'])
            news = models.NewsFeedItem.objects.get(id=int(request.POST['id']))
            news.delete()
            print "deleted!"
        except:
            pass
        return HttpResponse("")

    # Modify a newsfeed item
    # If we are modifying a feed...
    feed_id = int(request.POST['feed_id'])
    feed = ""
    if feed_id > 0:
        feed = models.NewsFeedItem.objects.get(id=feed_id)
        feed.title = request.POST['title']
        feed.body = request.POST['body']
        feed.subtitle = request.POST['nfsubtitle']
        feed.date_edited = datetime.utcnow().replace(tzinfo=utc)
        feed.save()

    # Saving a new newsfeed item
    else: 
        feed = models.NewsFeedItem(title=request.POST['title'],
                                   body=request.POST['body'],
                                   subtitle=request.POST['nfsubtitle'],
                                   business=profile,
                                   date=datetime.utcnow().replace(tzinfo=utc),
                                   date_edited=datetime.utcnow().replace(tzinfo=utc))
        feed.save()
        if request.POST['message_checkbox']=='on':
            for subscriber in profile.userprofile_set.all():
                print subscriber
                message = models.MessageItem(subject=request.POST['title'],
                                             text=request.POST['body'],
                                             sender=profile.user,
                                             business=profile,
                                             inbox=subscriber.user.inbox,
                                             date_created = datetime.utcnow().replace(tzinfo=utc))
                message.save()

    # Whether dealing with a new NewsFeedItem or not, deal with any uploaded
    # images.
    if 'nf_image' in request.FILES:
        print "Saving an image..."
        try:
            filename = '%s_%s_%s.jpg' % (profile.id,
                                         profile.business_name,
                                         feed.title[:10])
            save_image(feed.image, filename, request.FILES['nf_image'])
            feed.save()
        except IOError:
            pass
    messages.add_message(request, messages.SUCCESS, "Newsfeed items successfully created!")
    return HttpResponseRedirect(reverse("business_control_panel"))

# Returns all of a business' newsfeeds as JSON. To be called from AJAX.
@csrf_protect
@business_view
def newsfeed_list(request):
    profile = request.user.businessprofile

    feed = json.dumps(list(profile.newsfeeditem_set.all()),
                                   cls=views.NewsFeedItemEncoder)
    return HttpResponse(feed, mimetype="application/json")

# Blatantly stolen from a blog. Thanks!
def scale_dimensions(width, height, longest_side):
    ratio = 1.0
    if width > height:
        if width > longest_side:
            ratio = longest_side * 1.0/width
    elif height > width:
        ratio = longest_side * 1.0/height
    return (int(width*ratio), int(height*ratio))

# Also stolen! This makes saving an image to MEDIA_ROOT a bit more sensible.
def save_image(model_image, filename, tmp_image, thumbnail=False):
    '''
    Saves an image to a NewsFeedItem.

    model_image = Reference to the "image" field in a NewsFeedItem (or any model with an image).
    filename = Filename to use when saving the actual file
    tmp_image = The file that currently exists from uploading.
    '''
    feed_image = Image.open(tmp_image)
    (width, height) = feed_image.size
    print "width is...."+width
    print "height is....."+height
    
    #(width, height) = scale_dimensions(width, height, 70) 
    #feed_image = feed_image.resize((width, height))
    if thumbnail:
        # 4-tuple to give to feed_image
        thumbnail_size = 70
        box = ((width-thumbnal_size)/2,(height-thumbnail_size)/2,(width+thumbnail_size)/2, (height+thumbnail_size)/2)
        feed_image.crop()

    imagefile = StringIO.StringIO()
    feed_image.save(imagefile, 'JPEG')

    # give it a unique name
    filename_parts = filename.split('.')
    if thumbnail:
        filename = '%s%s.%s' % (filename_parts[0], hashlib.md5(imagefile.getvalue()).hexdigest(),'-thumbnail-', filename_parts[1]      
    else:
        filename = '%s%s.%s' % (filename_parts[0], hashlib.md5(imagefile.getvalue()).hexdigest(), filename_parts[1])      


    # save it to disk so we have a real file to work with
    imagefile = open(os.path.join('/tmp', filename), 'w')
    feed_image.save(imagefile,'JPEG')
    imagefile = open(os.path.join('/tmp',filename), 'r')
    content = File(imagefile)
    model_image.save(filename, content)



# The view that calls the control panel center, where a business can manage their employees, surveys and newsfeeds.
@business_view
def control_panel(request):
    
    profile = request.user.businessprofile
    
    if request.method == 'GET':
        # First all the employeees
        employee_list = profile.employeeprofile_set.order_by('user__last_name')
        
        # All the rating profiles for the business.
        rating_profile_list = profile.ratingprofile_set.all()

        # All the newsfeed items that have been created so far.
        newsfeed_list = profile.newsfeeditem_set.all()

        # The survey is a list of questions. Survey_list will be a list of surveys.
        survey_list = profile.survey_set.all()

        return render_to_response('business_control_panel.html',
                                  {'employee_list':employee_list,
                                   'rating_profile_list':rating_profile_list,
                                   'business_profile': profile,
                                   'feeds':newsfeed_list,
                                   'survey_list':survey_list},
                                  context_instance=RequestContext(request))
    # Method is post.
    else:
        return HttpResponseRedirect('/business/controlpanel')


@csrf_protect
@business_view
def rating_profile_changes(request):
    profile = request.user.businessprofile
    
    if request.method == 'POST':
        for emp_key, rating_val in json.loads(request.POST['emp_profile_change']).items():
            e = profile.employeeprofile_set.get(id=int(emp_key))
            p = profile.ratingprofile_set.get(id=int(rating_val))
            e.rating_profile=p
            e.save()
            
        messages.add_message(request, messages.SUCCESS, "The Rating Profiles have been successfully updated!")
    return HttpResponse('')


@csrf_protect
@business_view
def get_employee_info(request):
    profile = request.user.businessprofile
    if request.method == 'GET':
        employee=profile.employeeprofile_set.get(id=request.GET['emp_id'])
        return HttpResponse(json.dumps({'bio':employee.bio}),
                            mimetype='application/json')
            
    return render_to_response('business_control_panel.html',
                              {'employee':encoded_employee},
                              context_instance=RequestContext(request))

# Toggle a photo from active (shown to customers) to inactive,
# or vice versa.
@csrf_protect
@business_view
def toggle_photo(request):
    profile = request.user.businessprofile
    photo_id = request.POST['photo_id']
    photo = models.BusinessPhoto.objects.get(id=photo_id)
    photo.active = not photo.active
    photo.save()
    return HttpResponse('')
