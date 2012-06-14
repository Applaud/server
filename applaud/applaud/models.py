from django.db import models

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
	dimension, and the name of that dimension.
	'''

	# The title of the question or dimension of the rating,
	# e.g., 'smelliness' or 'How quick was your food?'
	# If a question, answer should be quantifiable.
	title = models.TextField(max_length=100)

	# Numeric value (response) for the question or dimension
	rating_value = models.IntegerField()

	# Employee to which this Rating corresponds
	employee = models.ForeignKey('Employee')

	def __unicode__(self):
		return "%s:%s"%(self.title,self.rating_value)

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

