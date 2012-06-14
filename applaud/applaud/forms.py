from django.forms import ModelForm
from django import forms
from applaud import models
from sets import Set
class NewsFeedItemForm(ModelForm):
	class Meta:
		model = models.NewsFeedItem

class EmployeeForm(ModelForm):
	
	class Meta:
		model = models.Employee

class RatingProfileForm(ModelForm):
	
	dimension = forms.Textarea()
	
	class Meta:
		model = models.RatingProfile
