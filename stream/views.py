from mapstream2.stream.forms import ReportEventForm
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.core.context_processors import csrf
from django.core.urlresolvers import resolve
from mapstream2.stream.models import EventReport, EventType, Event, SecureView
from django.contrib.auth.models import User
import json

def home(request):
	response = "Mapstream Server II v0.1"
	return HttpResponse(response)


def report_event(request):
	context = {}
	context.update(csrf(request))
	if request.method == 'POST':
		form = ReportEventForm(request.POST)
		if form.is_valid():
			clean_data = form.cleaned_data
			print "we have a report ... mwahahaha!"
			lat_long = clean_data['lat_long']
			lat, lon = lat_long.replace('(','').replace(')','').split(',')	# probably should use regex
			print 'we found lat: %s and long: %s' % (lat, lon)
			# create a new report (for the now the user defaults to tom)
			report = EventReport()
			report.title = "%s in %s" % (EventType.objects.get(id=1), clean_data['location'])
			report.made_by = User.objects.get(username='tom')
			report.confidence = 0.2		# default confidence level
			report.location = 'POINT(%s %s)' % (lon, lat)
			report.save()

			response = "we have location %s" % lat_long
			return HttpResponse(response)
		else:
			print 'form is not valid'
			form = ReportEventForm()
			context['form'] = form
	else:
		form = ReportEventForm()
		context['form'] = form
	return render_to_response('report_event.html', context)


def list_data(request, objectType, objectId=None):
	default = HttpResponse("Unknown object type requested")
	result = {
		"event": _list_event(request, objectId),
	}
	return result.get(objectType, default)

def secure_list_data(request, view_key):
	try:
		secure_view = SecureView.objects.get(key=view_key)
		url = secure_view.url
		view, args, kwargs = resolve(url)
		# kwargs['request'] = request
		print "fetch view for %s; with args %s" % (url, args)
		# run the view function
		return view(request, *args, **kwargs)
	except SecureView.DoesNotExist:
		return HttpResponse("Unknown view requested")


def _list_event(request, objectId):
	pretty = 'pretty' in request.GET
	if 'format' in request.GET and request.GET['format']:
		format = request.GET['format']
	else:
		format = 'display'	# display means ordinary json for now
	
	if objectId:
		try:
			cleanId = int(objectId)
			events = [Event.objects.get(id=cleanId)]
			if format == 'map':
				event_json = _prepare_map_json(request, events)
			else:
				event_json = serializers.serialize('json', events, indent=4 if pretty else None, sort_keys=pretty)
		except Event.DoesNotExist:
			event_json = 'No event exists with id: %s' % objectId
		except ValueError:
			data_source_json = 'The id "%s" is not a valid number' % objectId
		return HttpResponse(event_json, content_type='application/json')
	else:
		events = Event.objects.all()
		if format == 'map':
			event_json = _prepare_map_json(request, events)
		else:
			event_json = serializers.serialize('json', events, indent=4 if pretty else None, sort_keys=pretty)
		return HttpResponse(event_json, content_type='application/json')

def _prepare_map_json(request, events):
	pretty = 'pretty' in request.GET
	print 'formating for map!'
	results = []
	for event in events:
		map_event = {}
		map_event['name'] = event.name
		map_event['id'] = event.id
		map_event['type'] = "point"
		map_event['Longitude'] = '%s' % event.get_location()[1]
		map_event['Latitude'] = '%s' % event.get_location()[0]
		map_event['layer_id'] = 0 # using zero as the id for now
		results.append(map_event)
	map_json = json.dumps(results, indent=4 if pretty else None, sort_keys=pretty)
	return map_json