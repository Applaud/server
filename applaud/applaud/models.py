from django.db import models
import json

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

class Rating(models.Model):
	'''Models a rating. That is, a numeric value for a ratable
	dimension, and the name of that dimension. This is the result
	of answering some kind of prompt to rate an employee, for
	example.
	'''

	# The title of the question or dimension of the rating,
	# e.g., 'smelliness' or 'How quick was your food?'
	# If a question, answer should be quantifiable.
        # TODO: 
        # This seems a bit sloppy, make a foreign key to RatingProfile?
	title = models.TextField(max_length=100)

	# Numeric value (response) for the question or dimension
	rating_value = models.FloatField()

	# Employee to which this Rating corresponds
	employee = models.ForeignKey('Employee')

	def __unicode__(self):
		return "%s:%s"%(self.title,self.rating_value)

class RatingProfile(models.Model):
	'''Models what dimensions are relevant to a specific employee.
	'''
	title = models.TextField(max_length=100)
	dimensions = SerializedStringsField()

        def __unicode__(self):
            return self.title

class NewsFeedItem(models.Model):
	'''Models an item in the newsfeed.
	'''
	title = models.CharField(max_length=100)
	subtitle = models.TextField(max_length=100)
	body = models.TextField(max_length=500)
	date = models.DateTimeField(editable=False)

class Employee(models.Model):
	'''Models an employee.
	'''
	first_name = models.TextField(max_length=100)
	last_name = models.TextField(max_length=100)

        bio = models.TextField(max_length=1000,blank=True,null=True)

	# What dimensions are relevant for rating this employee
	rating_profile = models.ForeignKey(RatingProfile)

class GeneralFeedback(models.Model):
    '''Gives general feedback on a location.
    '''
    feedback = models.TextField()

#################
# SURVEY MODELS #
#################

class Survey(models.Model):
    title = models.TextField(max_length=100)
    description = models.TextField(max_length=1000,blank=True,null=True)

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

    # Type of widget for the question
    type = models.CharField(max_length=2,choices=QUESTION_TYPES)

    # Labels for multiple-choice type questions
    options = SerializedStringsField()

    # The survey to which this question belongs
    survey = models.ForeignKey(Survey)

    # TODO: perhaps have a field for default value?

    def __unicode__(self):
        return self.label

class QuestionResponse(models.Model):
    # What question are we responding to?
    question = models.ForeignKey(Question)

    # The reponse. Should be interpreted about whatever question.type is.
    response = SerializedStringsField()

    def __unicode__(self):
        return json.dumps(self.response)


###############
# USER MODELS #
###############
