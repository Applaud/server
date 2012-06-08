from django.models import Model

class Business:
	google_places_id = TextField(required=True, blank=False)
	business_type = TextField()
	name = TextField(required=True, blank=False)

class Survey:
	title = TextField(required=True, blank=False)
	description = TextField()

class Question:
	survey = models.ForeignKey('Survey')
	prompt = TextField(required=True,blank=False)
	question_type = TextField(required=True, blank=False)
	options = TextField(max_chars=500, required=True, blank=False)
