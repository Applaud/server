from django.forms import ModelForm
from applaud import models

class NewsFeedItemForm(ModelForm):
	class Meta:
	    model = models.NewsFeedItem
