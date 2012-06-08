from django.shortcuts include render_to_response

def home(request):
	return render_to_response('/templates/home.html', {})
