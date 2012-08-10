from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from applaud.models import RatingProfile, BusinessProfile, EmployeeProfile, Inbox, MessageItem
from django.core.urlresolvers import reverse
from django.template import RequestContext, Template
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.middleware.csrf import get_token

from datetime import datetime, timedelta
from django.utils.timezone import utc

from django.contrib.auth.models import Group, User
import sys
import json
import urllib2
from applaud import forms
from applaud import models
import employee_views
import business_views
from registration import forms as registration_forms
import settings
import datetime

def index(request):
    user_type = ''
    profile = ""
    if request.user.is_authenticated():
	# Are we a business?
	try:
	    profile = request.user.businessprofile
            user_type = 'business'
	except BusinessProfile.DoesNotExist:
	    try:
                profile = request.user.employeeprofile
                user_type = 'employee'
            except EmployeeProfile.DoesNotExist:
                user_type = 'user'
    return render_to_response('index.html', {'user': request.user,
                                             'user_type': user_type},
                              context_instance=RequestContext(request))

# Encodes a poll
class SimplePollEncoder(json.JSONEncoder):
    '''SimplePollEncoder

    Encodes a Poll object into JSON, giving a simple representation of PollResponses
    given for this Poll. A more complex PollEncoder might give more complete information
    on PollResponses, such as when the response was made and who made it.
    '''
    def default(self,o):
        if isinstance(o, models.Poll):
            # Count up number of responses for each option
            responses = []
            counter = 0
            for option in o.options:
                responses.append({"title":option,
                                  "count":len(models.PollResponse.objects.filter(poll=o, value=counter))})
                counter += 1
    
            votes = o.votes.all()
            user_rating = 0
            for v in votes:
                user_rating += 1 if v.positive else -1
            res = { 'title':o.title,
                    'options':o.options,
                    'user_creator':UserProfileEncoder().default(o.user_creator) if o.user_creator is not None else "",
                    'responses':responses,
                    'date_created':o.date_created.strftime("%m/%d/%Y %H:%M:%S"),
                    'user_rating':user_rating,
                    'business_id':o.business.id,
                    'id':o.id }
            return res
        else:
            return json.JSONEncoder.default(self, o)    
        

# Encodes a Thread
class ThreadEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Thread):
            encoder = ThreadPostEncoder()
            upvotes = len(o.votes.filter(positive=True))
            downvotes = len(o.votes.all())-upvotes
            res = {'title':o.title,
                   'date_created':o.date_created.strftime("%m/%d/%Y %H:%M:%S"),
                   'user_creator':UserProfileEncoder().default(o.user_creator) if o.user_creator is not None else "",
                   'upvotes':upvotes,
                   'downvotes':downvotes,
                   'posts':[encoder.default(p) for p in o.threadpost_set.all()],
                   'id':o.id}
            return res
        else:
            return json.JSONEncoder.default(self, o)

# Encodes a ThreadPost. Used by the ThreadEncoder
class ThreadPostEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.ThreadPost):
            upvotes = len(o.votes.filter(positive=True))
            downvotes = len(o.votes.all())-upvotes
            res = {'body':o.body,
                   'user':UserProfileEncoder().default(o.user),
                   'date_created':o.date_created.strftime("%m/%d/%Y %H:%M:%S"),
                   'upvotes':upvotes,
                   'downvotes':downvotes,
                   'id':o.id}
            return res
        else:
            return json.JSONEncoder.default(self, o)
                
# Encodes a RatingProfile into JSON format
class RatingProfileEncoder(json.JSONEncoder):
    def default(self, o):
	if isinstance(o, models.RatingProfile):
            dim_enc = RatedDimensionEncoder()
	    res = {'title': o.title,
                   'dimensions': [dim_enc.default(dim) for dim in o.rateddimension_set.all()],
                   'business_id': o.business.id,
                   'id':o.id }
	    return res
	else:
	    return json.JSONEncoder.default(self, o)

class RatedDimensionEncoder(json.JSONEncoder):
    def default(self, o):
	if isinstance(o, models.RatedDimension):
            return {'title': o.title,
                    'active': o.is_active,
                    'is_text': o.is_text,
                    'id':o.id}
	else:
	    return json.JSONEncoder.default(self, o)

# Encodes an Employee into JSON format
class EmployeeEncoder(json.JSONEncoder):
    def default(self, o):
	if isinstance(o, models.EmployeeProfile):
            dimension_encoder = RatedDimensionEncoder()
            dimension_list = []
            for d in o.rating_profile.rateddimension_set.all():
                dimension_list.append(dimension_encoder.default(d))
            image_url = employee_views._profile_picture(o)
            if image_url:
                image_url = settings.MEDIA_URL+image_url
	    res = {'first_name':o.user.first_name,
		   'last_name':o.user.last_name,
		   'bio':o.bio,
		   'ratings':
		       {'rating_title':"" if o.rating_profile.title is None else o.rating_profile.title,
			'dimensions':dimension_list},
                   'image':image_url,
                   'id':o.id
		   }
	    return res
	else:
	    return json.JSONEncoder.default(self, o)

# Encodes a UserProfile into JSON format
class UserProfileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.UserProfile):
            return {'first_name':o.user.first_name,
                    'last_name':o.user.last_name,
                    'username':o.user.username,
                    'birth':o.date_of_birth.strftime("%m/%d/%Y"),
                    'id':o.id}
        else:
            return json.JSONEncoder.default(self, o)

# Encodes a BusinessProfile into JSON format
class BusinessProfileEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.BusinessProfile):
            bus_user = o.user
            logo_url = '%s%s' % (settings.MEDIA_URL, settings.DEFAULT_PROFILE_IMAGE)
            if o.logo:
                logo_url = o.logo.url
            res = {'name': o.business_name,
                   'goog_id': o.goog_id,
                   'business_id': o.id,
                   'latitude': o.latitude,
                   'longitude': o.longitude,
                   'phone': o.phone,
                   'logo': logo_url,
                   'primary': o.primary_color,
                   'secondary': o.secondary_color,
                   'generic': not o.user.is_active}
            return res
        else:
            return json.JSONEncoder.default(self, o)

# Encodes a Survey into JSON format
class SurveyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Survey):
            question_list = list(o.question_set.all())
            questions = []
            question_encoder = QuestionEncoder()
            for q in question_list:
                questions.append(question_encoder.default(q))
            res = {'title': o.title,
                   'id':o.id,
                   'description': o.description,
                   'questions': questions}
            return res
        else:
            return json.JSONEncoder.default(self, o)

# Encodes a Question into JSON.
class QuestionEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Question):
            return {'label': o.label,
                    'type': o.type,
                    'options': o.options,
                    'general_feedback': o.general_feedback,
                    'active': o.active,
                    'id': o.id}
        else:
            return json.JSONEncoder.default(self, o)


# Encodes a question response into JSON
class QuestionResponseEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.QuestionResponse):
            return {'date': o.date_created.strftime('%m/%d/%Y'),
                    'response': o.response,
                    'user': UserProfileEncoder().default(o.user)}
        else:
            return json.JSONEncdoder.default(self, o)


# Encodes a NewsFeedItem into JSON.
class NewsFeedItemEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.NewsFeedItem):
            image_url = ""
            if o.image:
                image_url = o.image.url
            return {'id': o.id,
                    'title': o.title,
                    'subtitle': o.subtitle,
                    'body': o.body,
                    'date': o.date.strftime('%m/%d/%Y'),
                    'business': o.business.business_name,
                    'image': image_url,
                    'date_edited':o.date_edited.strftime('%m/%d/%Y')}
        else:
            return json.JSONEncoder.default(self, o)

class RatingEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Rating):
            return {'value':o.rating_value,
                    'user':UserProfileEncoder().default(o.user),
                    'date':o.date_created.strftime("%m/%d/%Y"),
                    'title':o.title}
        else:
            return json.JSONEncoder.default(self, o)


class MessageItemEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o, models.MessageItem):
            print o.subject
            print o.date_created
            return {'subject':o.subject,
                    'text':o.text,
                    'date':o.date_created.strftime("%m/%d/%Y"),
                    'unread':o.unread,
                    'sender': {'first_name':o.sender.first_name,
                               'last_name':o.sender.last_name,
                               'id':o.sender.id}}
        else:
            return json.JSONEncoder.default(self, o)

class BusinessPhotoEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, models.BusinessPhoto):
            return {'image': o.image.url,
                    'business': o.business.id,
                    'tags': o.tags,
                    'upvotes': o.upvotes,
                    'downvotes': o.downvotes,
                    'active': o.active,
                    'uploaded_by': UserProfileEncoder().default(o.uploaded_by)}
        else:
            return json.JSONEncoder.default(self, o)

def view_inbox(request):
    
    if request.user.is_authenticated():
        # try:
        #     profile = request.user.businessprofile
        # except BusinessProfile.DoesNotExist:
        #     try:
        #         profile = request.user.employeeprofile
        #     except EmployeeProfile.DoesNotExist:
        #         profile = request.user.userprofile
        inbox = request.user.inbox
        message_list = inbox.messageitem_set.all()
        return render_to_response('messages.html',
                                  {'message_list':message_list,
                                   'user':request.user},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse("auth_login"))

@csrf_protect
def get_inbox(request):
    if request.method == 'GET':
        inbox = request.user.inbox
        return_data={}
        for mess in inbox.messageitem_set.all():
            print "before"
            print mess
            encoded_message = MessageItemEncoder().default(mess)
            if not 'messages' in return_data:
                return_data['messages']=[encoded_message]
            else:
                return_data['messages'].append(encoded_message)
            mess.unread = False
            mess.save()
        print "outside for loop"
        print return_data
        return HttpResponse(json.dumps({'inbox_data':return_data}),
                            mimetype="application/json")
    
    return HttpResponseRedirect('/messages')


# BAD BAD BAD. Fix this!
@csrf_exempt
def send_message(request):
    '''
    {'sender_id':user_id,
     'recipient_id': ... ,
     'subject': ... ,
     'text': ... }
     '''
    if request.method=='POST':
        s = User.objects.get(id=request.POST['sender_id'])
        recipient = User.objects.get(id=request.POST['recipient_id'])
        i = recipient.inbox
        message = models.MessageItem(text=request.POST['text'], 
                                     subject=request.POST['subject'],
                                     date_created=datetime.datetime.utcnow().replace(tzinfo=utc),
                                     sender = s,
                                     inbox = i)
        print message.date_created.date()
        message.save()
    return HttpResponse('')

