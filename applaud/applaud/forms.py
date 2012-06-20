from django.forms import ModelForm
from django import forms
from applaud import models
from sets import Set
class NewsFeedItemForm(ModelForm):
	class Meta:
		model = models.NewsFeedItem
                exclude = ('business',)
                
class EmployeeForm(ModelForm):
	
	class Meta:
		model = models.Employee
		exclude = ('business',)

class RatingProfileForm(ModelForm):
	
	dimension = forms.Textarea()
	
	class Meta:
		model = models.RatingProfile

class SurveyCreateForm(ModelForm):
	question = forms.Textarea()
	option = forms.Textarea()

	class Meta:
		model = models.Survey
