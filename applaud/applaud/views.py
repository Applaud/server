from django.shortcuts import render_to_response
from django.http import HttpResponse
import json

def home(request):
	return render_to_response('home.html')

def example(request):
	res = { "nearby_businesses": [] }
	return HttpResponse(json.dumps(res))

def example2(request):
	res = { "nearby_businesses": [
			{"name":"Foo Burgers",
			 "type":"Burgers",
			 "goog_id":"677679492a58049a7eae079e0890897eb953d79b",
			 "latitude":39.981634,
			 "longitude":-83.004617},
			]
		}
	return HttpResponse(json.dumps(res))

def example3(request):
	res = { "nearby_businesses":
			[
			{"name":"Foo Burgers",
			 "type":"Burgers",
			 "goog_id":"677679492a58049a7eae079e0890897eb953d79b",
			 "latitude":39.981634,
			 "longitude":-83.004617},
			{"name":"Seymour House of Smiles",
			 "type":"Orthodontist",
			 "goog_id":"27ea39c8fed1c0437069066b8dccf958a2d06f19",
			 "latitude":39.981934,
			 "longitude":-83.004676},
			],
		}
	return HttpResponse(json.dumps(res))

	#return render_to_response('example_rcvplace3.json', mimetype='application/json')


def checkin(request, lat, lon):
	try:
	    lat = float(lat)
	    lon = float(lon)
	except:
	    #
	    pass

	


	return render_to_response('checkin.html',{'lat':lat,'long':lon})	
