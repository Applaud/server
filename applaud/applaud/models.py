from django.db import models

class NewsFeedItem(models.Model):
	title = models.CharField(max_length=100)
	sub_title = models.TextField(max_length=100)
	body = models.TextField(max_length=500)
	
	def __init__(self, vals):
		self.title=vals["title"]
		self.sub_title=vals["sub_title"]
		self.body=vals["body"]

