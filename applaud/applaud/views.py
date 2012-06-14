from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
import json
import urllib2
from applaud import forms
from applaud import models
from applaud.models import RatingProfile
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
import sys

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

# This allows a user to save and view newsfeed posts
@csrf_protect
def formtest(request):
	if request.method == 'POST':
	    n = forms.NewsFeedItemForm(request.POST)
	    newsitem = n.save(commit=False)
	    newsitem.date = datetime.now()
	    newsitem.save()
	    
	f = forms.NewsFeedItemForm()
	newsfeed = models.NewsFeedItem.objects.all()
	
	return render_to_response('basic_newsfeed.html',
				  {'form':f, 'list':newsfeed},
				  context_instance=RequestContext(request))
	
def nfdata(request):
	# TODO: access newsfeed for a particular business
	# 
	# if ( request.GET ):
	# 	business_id = request.GET['business_id']

	nfitems = models.NewsFeedItem.objects.all()
	nfitem_list = []
	for nfitem in nfitems :
		nfitem_list.append({'title':nfitem.title,
				    'subtitle':nfitem.subtitle,
				    'body':nfitem.body,
				    'date':str(nfitem.date)})

	ret = { 'newsfeed_items':nfitem_list }

	return HttpResponse(json.dumps(ret))

@csrf_protect
def create_employee(request):
	if ( request.POST ):
		employee_form = forms.EmployeeForm(request.POST)
		employee_form.save()

	new_form = forms.EmployeeForm()
	employees = models.Employee.objects.all()

	return render_to_response('employees.html',
				  {'form':new_form, 'list':employees},
				  context_instance=RequestContext(request))

class EmployeeEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, models.Employee):
			res = {'first_name':o.first_name,
			       'last_name':o.last_name}
			return res
		else:
			return json.JSONEncoder.default(self, o)

def employee_list(request):
	return HttpResponse(json.dumps({'employees':list(models.Employee.objects.all())},
				       cls=EmployeeEncoder),
			    mimetype='application/json')

@csrf_protect
def create_rating_profile(request):
    '''Create a rating profile.
    Takes a variable number of text fields and turns them into dimensions
    for a rating profile. Also includes the title.
    '''
    # if not request.user.is_authenticated():
    #     return HttpResponseRedirect('/login')
    if request.method == 'GET':
        return render_to_response('employeeprofile_create.html',
                                  {},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
	sys.stderr.write(str(request.POST))
        i = 0
        dimensions = []
        while 'dimension_' + str(i) in request.POST and request.POST['dimension_' + str(i)]:
            dimensions.append(request.POST['dimension_' + str(i)])
            i += 1
        title = ''
        if 'title' in request.POST and request.POST['title']:
            title = request.POST['title']
        errors = {}
        err = False
        if not title:
            errors['title_err'] = "You should enter a title for this rating profile."
            err = True
        if not dimensions:
            errors['dimensions_err'] = "No dimensions?"
            err = True
        if err:
            errors['dimensions'] = dimensions
            return render_to_response('create_rating_profile.html',
                                      errors,
                                      context_instance=RequestContext(request))
        rp = RatingProfile(title=title, dimensions=dimensions)
        rp.save()
	
        return HttpResponseRedirect('/ratingprofiles')

@csrf_protect
def list_rating_profiles(request):
	l = list(RatingProfile.objects.all())
	ret = []
	for item in l:
		ap = {}
		ap['title']=item.title
		ap['dimensions']=item.dimensions
		ret.append(ap)
	
	return render_to_response('employeeprofile_create.html',
				  {'list':ret},
				  context_instance=RequestContext(request))

