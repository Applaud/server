from django.forms import ModelForm, forms
from applaud import models

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
