from mapstream2.stream.forms import ReportEventForm
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.core.context_processors import csrf
from django.core.urlresolvers import resolve
from mapstream2.stream.models import EventReport, EventType, Event, SecureView
from django.contrib.auth.models import User
import json, time, datetime

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


def list_data(request, objectType, objectId=None, secure_params=None):
	# try to load a secure view if the object type is unknown
	default = lambda: secure_list_data(request, objectType)
	result = {
		"event": _list_event(request, objectId, secure_params=secure_params),
		"map_settings": get_map_settings(request, secure_params=secure_params),
	}
	return result.get(objectType, default())

def secure_list_data(request, view_key):
	# return HttpResponse('try to show a secure view')
	try:
		secure_view = SecureView.objects.get(key=view_key)
		url = secure_view.url
		view, args, kwargs = resolve(url)

		# add each parameter to the request GET
		params = secure_view.parameters.all()
		if params:
			param_list = {}
			for param in params:
				param_list[param.keyword] = param.value # THIS IS IMMUTABLE ... nooooooo
			kwargs['secure_params'] = param_list

		for a in args:
			print "arg: %s" % a

		print "fetch view %s for %s; with args %s" % (view, url, args)
		# run the view function
		return view(request, *args, **kwargs)
	except SecureView.DoesNotExist:
		return HttpResponse("Unknown object requested")


def _list_event(request, objectId, secure_params=None):
	parameters = _choose_parameters(request, secure_params)
	pretty = 'pretty' in parameters
	print 'pretty is in params'
	if 'format' in parameters and parameters['format']:
		format = parameters['format']
	else:
		format = 'display'	# display means ordinary json for now
	
	if objectId:
		try:
			cleanId = int(objectId)
			events = [Event.objects.get(id=cleanId)]
			if format == 'map':
				event_json = _prepare_map_json(request, events, secure_params)
			else:
				event_json = serializers.serialize('json', events, indent=4 if pretty else None, sort_keys=pretty)
		except Event.DoesNotExist:
			event_json = 'No event exists with id: %s' % objectId
		except ValueError:
			event_source_json = 'The id "%s" is not a valid number' % objectId
		return HttpResponse(event_json, content_type='application/json')
	else:
		if 'ts' in request.GET and request.GET['ts']:
			try:
				print "timestamp sting is %s" % request.GET['ts']
				time_stamp = datetime.datetime.fromtimestamp(float(request.GET['ts']))
				print "we got timestamp: %s" % (time_stamp)
				events = Event.objects.filter(updated_at__gte=time_stamp)
			except ValueError:
				events = Event.objects.all()
		else:
			events = Event.objects.all()
		if format == 'map':
			event_json = _prepare_map_json(request, events, secure_params)
		else:
			event_json = serializers.serialize('json', events, indent=4 if pretty else None, sort_keys=pretty)
		return HttpResponse(event_json, content_type='application/json')

def _prepare_map_json(request, events, secure_params=None):
	parameters = _choose_parameters(request, secure_params)
	pretty = 'pretty' in parameters
	print 'formating for map!'
	results = []
	for event in events:
		map_event = {}
		map_event['name'] = event.name
		map_event['id'] = event.id
		map_event['type'] = "point"
		map_event['Longitude'] = '%s' % event.location.coords[0]
		map_event['Latitude'] = '%s' % event.location.coords[1]
		map_event['layer_id'] = event.event_type.id
		results.append(map_event)
	map_result = {
		"timestamp": time.time(),
		"events": results,
	}
	map_json = json.dumps(map_result, indent=4 if pretty else None, sort_keys=pretty)
	return map_json

def _choose_parameters(request, secure_params):
	if secure_params:
		return secure_params
	else:
		return request.GET

def get_map_settings(request, secure_params=None):
	parameters = _choose_parameters(request, secure_params)
	pretty = 'pretty' in parameters

	settings = {}
	layer_list = []
	level_list = []
	for event_type in EventType.objects.all():
		layer = {
			"id": event_type.id,
			"label": event_type.name,
			"description": event_type.description,
			"color": event_type.colour,
		}
		layer_list.append(layer)
	# for now return some default level
	level = {
		"id": 0,
		"label": "Parish",
		"max_zoom": 25,
		"color": "#00c0ff",
	}
	level_list.append(level)
	settings = {
		"layer": layer_list,
		"level": level_list,
	}
	settings_json = json.dumps(settings, indent=4 if pretty else None, sort_keys=pretty)
	return HttpResponse(settings_json, content_type='application/json')