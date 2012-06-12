from django.shortcuts import render_to_response

def home(request):
	return render_to_response('home.html', {})

def example(request):
	return render_to_response('example_rcvplace.json', mimetype='application/json')

def example2(request):
	return render_to_response('example_rcvplace2.json', mimetype='application/json')

def example3(request):
	return render_to_response('example_rcvplace3.json', mimetype='application/json')

