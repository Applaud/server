from django.shortcuts import render_to_response
from django.http import HttpResponse
import json
import urllib2

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


def checkin(request):
	if not "latitude" in request.GET or not  "longitude" in request.GET:
	    error = "Latitude & longitude confusion...."
	    return render_to_response('error.html',{"error":error})   

	lat = request.GET["latitude"]
	lon = request.GET["longitude"]	

	goog_api_key="AIzaSyCbw9_6Mokk_mKwnH02OYyB6t5MrepFV_E"
	radius="100"

	from_goog = urllib2.urlopen("https://maps.googleapis.com/maps/api/place/search/json?location="+lat+","+lon+"&radius="+radius+"&sensor=false&key="+goog_api_key)

	to_parse = json.loads(from_goog.read())
	#return HttpResponse(to_parse)

	ret = {"nearby_businesses":[],}

	for entry in to_parse["results"]:
		new_biz={"name":entry["name"],
			 "type":entry["types"][0],
			 "goog_id":entry["id"],
			 "latitude":entry["geometry"]["location"]["lat"],
			 "longitude":entry["geometry"]["location"]["lng"]}
		ret["nearby_businesses"].append(new_biz)
	ret = json.dumps(ret)
	return HttpResponse(ret)
