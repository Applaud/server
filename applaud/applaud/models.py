from django.contrib.auth.models import User
from django.forms import ValidationError
from django.db import models
import json
from applaud import settings

#
# CUSTOM MODEL FIELDS
#

class SerializedStringsField(models.TextField):
    """Allows us to store a list of strings
    directly in the database using JSON to
    serialize/deserialize."""

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(SerializedStringsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return json.loads(value)

    def get_prep_value(self, value):
        if not value:
            return '[]'
        assert(isinstance(value, list) or isinstance(value, tuple))
        return json.dumps(value)

class SerializedRatingsField(models.TextField):
    """Allows us to store a list of Ratings
    directly in the database using JSON to
    serialize/deserialize."""

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(SerializedRatingsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return
        if isinstance(value, list):
            return value
        return json.loads(value)

    def get_prep_value(self, value):
        if not value:
            return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return json.dumps(value)

# 
# POLLS
#
class Poll(models.Model):
    '''Models a poll. A Poll is a user-posed single-select, multiple-choice question
    for which the results are displayed to the user upon submission.
    '''

    # Title of the poll
    title = models.TextField(max_length=100)

    # Rating of this poll (how well-liked it is)
    votes = models.ManyToManyField('Vote')

    # Business this poll is for
    business = models.ForeignKey('BusinessProfile')

    # Labels for multiple-choice type questions
    options = SerializedStringsField()

    # When this poll was created
    date_created = models.DateTimeField(auto_now=True)

    # User who created the poll, if there was one
    user_creator = models.ForeignKey('UserProfile', blank=True, null=True)

    def __unicode__(self):
        return self.title

class PollResponse(models.Model):
    '''Models a response to a Poll. See above.
    '''

    user = models.ForeignKey('UserProfile')
    value = models.IntegerField()
    poll = models.ForeignKey('Poll')
    date_created = models.DateField(blank=True, null=True)

#
# EMPLOYEE RATINGS
#
class Rating(models.Model):
	'''Models a rating. That is, a numeric value for a ratable
	dimension, and the name of that dimension. This is the result
	of answering some kind of prompt to rate an employee, for
	example.
	'''

	# The title of the question or dimension of the rating,
	# e.g., 'smelliness' or 'How quick was your food?'
	# If a question, answer should be quantifiable.
	title = models.TextField(max_length=100)

        # What dimension this rating is for
        dimension = models.ForeignKey('RatedDimension')

	# Numeric value (response) for the question or dimension
	rating_value = models.FloatField(blank=True, null=True)
        
        # Text value (response)
        rating_text = models.TextField(blank=True, null=True)
        
	# Employee to which this Rating corresponds
	employee = models.ForeignKey('EmployeeProfile')

        # End user who provided the response
        user = models.ForeignKey('UserProfile')

        date_created = models.DateTimeField()

        # Gives the rating rounded to one decimal place
        def rounded_rating(self):
            return float('%.1f' % round(self.rating_value,1)) if self.rating_value else 0
        
	def __unicode__(self):
		return "%s:%s (%s)"%(self.title,
                                     self.rating_value,
                                     self.date_created.strftime("%d/%m/%Y"))

class RatingProfile(models.Model):
    '''Models what dimensions are relevant to a specific employee.
    '''
    title = models.TextField(max_length=100)
    business = models.ForeignKey('BusinessProfile')

    def __init__(self, *args, **kwargs):
        super(RatingProfile, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # No empty titles
        if self.title != "":
            super(RatingProfile, self).save(*args, **kwargs)

            # Make sure we still have 'Quality' as a dimension
            self.validate()

    def validate(self):
        if not 'Quality' in [t.title  for t in self.rateddimension_set.all()]:
            r = RatedDimension(title='Quality',
                               rating_profile=self)
            r.save()

        if not 'Comments:' in [t.title  for t in self.rateddimension_set.all()]:
            r = RatedDimension(title='Comments:',
                               rating_profile=self,
                               is_text=True)
            r.save()


    def __unicode__(self):
        return self.title
    

class RatedDimension(models.Model):
    title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=1)
    rating_profile = models.ForeignKey('RatingProfile')
    is_text = models.BooleanField(default=0)
    
    def __unicode__(self):
        return self.title

#
# NEWSFEED
#
class NewsFeedItem(models.Model):
	'''Models an item in the newsfeed.
	'''
	title = models.CharField(max_length=100)
	subtitle = models.TextField(max_length=100)
	body = models.TextField(max_length=500)
	date = models.DateTimeField(editable=False)
        business = models.ForeignKey('BusinessProfile')
        image = models.ImageField(blank=True, null=True, upload_to='newsfeed_pictures/')
        date_edited = models.DateTimeField()

        def change_parameters(self, d):
            for key, value in d.iteritems():
                if key != 'id':
                    setattr(self, key, value)
        
        def __unicode__(self):
            return '%s at %s' % (self.title, self.business)

#
# GENERAL FEEDBACK
#
class GeneralFeedback(models.Model):
    '''Gives general feedback on a location.
    '''
    feedback = models.TextField(max_length=10000)
    business = models.ForeignKey('BusinessProfile')
    date_created=models.DateTimeField()
    user = models.ForeignKey('UserProfile')

#
# SURVEY MODELS
#
FEEDBACK_LABEL = 'Share Your Thoughts'
class Survey(models.Model):
    title = models.TextField(max_length=100)
    description = models.TextField(max_length=1000,blank=True,null=True)
    business = models.ForeignKey('BusinessProfile')

    def save(self, *args, **kwargs):
        super(Survey, self).save(*args, **kwargs)

        # Make sure we have a general feedback question
        self.validate()

    def validate(self):
        # Every survey has a "General Feedback" question
        general_feedback_questions = list(self.question_set.filter(general_feedback=True))
        if len(general_feedback_questions) == 0:
            q = Question(label=FEEDBACK_LABEL,
                         type='TA',
                         general_feedback=True,
                         survey=self,
                         options=[])
            q.save()
        else:
            feedback = general_feedback_questions.get[0]
            feedback.label = FEEDBACK_LABEL
            feedback.save()

    def __unicode__(self):
        return self.title

class Question(models.Model):
    # Question text
    label = models.TextField(max_length=200)

    # Types of widgets that are available
    QUESTION_TYPES = (
        ('TA', 'textarea'),
        ('TF', 'textfield'),
        ('RG', 'radio group'),
        ('CG', 'checkbox group'),
    )

    # Is this a general feedback question?
    general_feedback = models.BooleanField(default=0)

    # Type of widget for the question
    type = models.CharField(max_length=2,choices=QUESTION_TYPES)

    # Labels for multiple-choice type questions
    options = SerializedStringsField()

    # Whether this question is active or not
    active = models.BooleanField(default=1)

    # The survey to which this question belongs
    survey = models.ForeignKey(Survey)
    
    def __unicode__(self):
        return self.label

class QuestionResponse(models.Model):
    # What question are we responding to?
    question = models.ForeignKey(Question)

    # The response. Should be interpreted about whatever question.type is.
    # Why is this a serialized strings field??
    response = SerializedStringsField()
    
    # The end user who provided the response
    user = models.ForeignKey('UserProfile')

    date_created=models.DateTimeField()
    def __unicode__(self):
        return json.dumps(self.response)


#
# PROFILES
#
class BusinessProfile(models.Model):
    # N.B. The business name is stored as 'username' in the corresponding
    # User object.

    business_name = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=14,blank=True,null=True)
    user = models.OneToOneField(User)
    address = models.CharField(max_length=500)
    first_time = models.BooleanField(default=1)
    logo = models.ImageField(blank=True, null=True, upload_to='business_logos/')
    
    # The colors for this business. Stored as a ColorField, which is documented
    # up at the top of this file.
    primary_color = models.CharField(default=settings.DEFAULT_PRIMARY_COLOR,max_length=7)
    secondary_color = models.CharField(default=settings.DEFAULT_SECONDARY_COLOR,max_length=7)

    # This is used to store the unique ID from Google Places.
    # This is ONLY used to see if we have a location from GP in the Applaud database.
    # After that, the ID of BusinessProfile is used to uniquely identify a business.
    # Except when signing employees up
    goog_id = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s (%s)"%(self.user.username,self.address)

class EmployeeProfile(models.Model):
    '''Models an employee.
    '''
    # Just a standard bio for an employee
    bio = models.TextField(max_length=300,blank=True,null=True)
    # What dimensions are relevant for rating this employee
    rating_profile = models.ForeignKey(RatingProfile, blank=True, null=True)
    # Where does this employee work?
    business = models.ForeignKey('BusinessProfile')
    user = models.OneToOneField(User)

    first_time = models.BooleanField(default=1)

    profile_picture = models.ImageField(blank=True, null=True, upload_to=settings.MEDIA_ROOT)

    def __unicode__(self):
        return '%s %s %s' % (self.user.first_name, self.user.last_name, self.user)

    def change_parameters(self, d):
        for key, value in d.iteritems():
            if key != 'id':
                setattr(self, key, value)
 
# Model for the end user.
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    date_of_birth = models.DateField(blank=True, null=True)
    first_time = models.BooleanField(default=1)
    
    # Other valuable information that we can get from the user.
    SEX_TYPES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        )
    sex = models.CharField(max_length=6, choices=SEX_TYPES, blank=True, null=True)
    businesses_followed = models.ManyToManyField(BusinessProfile, blank=True, null=True)
    def __unicode__(self):
        return '%s %s %s' % (self.user.first_name, self.user.last_name, self.user)

    def change_parameters(self, d):
        for key, value in d.iteritems():
            if key != 'id':
                setattr(self, key, value)

class BusinessPhoto(models.Model):
    """
    A photo for a business.
    
    tags is a list of strings which describe this photo.
    votes is a signed integer showing the aggregate votes this photo has received.
    active is a boolean indicating whether or not this photo will be shown to users.
    uploaded_by is the user who uploaded this photo.
    """
    image = models.ImageField(blank=True, null=True, upload_to='business_photos/')
    business = models.ForeignKey('BusinessProfile')
    tags = SerializedStringsField()
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    active = models.BooleanField(default=0)
    uploaded_by = models.ForeignKey('UserProfile')
# # This needs to be implemented
# class CorporateProfile(request):
    
# It's called MessageItem because messages was making django fussy
class MessageItem(models.Model):
    subject = models.TextField(max_length=100, blank=True, null=True, default=" ")
    text = models.TextField(default=" ")

    # we don't need to recipient because the message belongs to one inbox
    sender = models.ForeignKey(User)

    # the business related to the sender (if it's either a business itself or employee)
    business = models.ForeignKey('BusinessProfile', blank=True, null=True)

    unread = models.BooleanField(default=1)

    inbox = models.ForeignKey('Inbox')
    date_created=models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.text


class Inbox(models.Model):
    user = models.OneToOneField(User)
    def __unicode__(self):
        return str(self.user)

class Vote(models.Model):
    positive = models.BooleanField()
    date_created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('UserProfile')

    def __unicode__(self):
        return self.user.user.first_name + self.user.user.last_name + "+" if self.positive else "-"
