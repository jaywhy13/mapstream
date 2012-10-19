from stream.forms import ReportEventForm
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.core.context_processors import csrf
from django.core.urlresolvers import resolve
from stream.models import EventReport, EventType, Event, SecureView
from django.contrib.auth.models import User
import json, time, datetime
from django.db.models import Q, Count

def home(request):
	response = "Mapstream Server II v0.2"
	return HttpResponse(response)


def report_event(request):
	context = {}
	context.update(csrf(request))
	if request.method == 'POST':
		form = ReportEventForm(request.POST)
		if form.is_valid():
			clean_data = form.cleaned_data
			#print "we have a report ... mwahahaha!"
			lat_long = clean_data['lat_long']
			lat, lon = lat_long.replace('(','').replace(')','').split(',')	# probably should use regex
			#print 'we found lat: %s and long: %s' % (lat, lon)
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
			#print 'form is not valid'
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

		#for a in args:
			#print "arg: %s" % a

		#print "fetch view %s for %s; with args %s" % (view, url, args)
			# run the view function
		return view(request, *args, **kwargs)
	except SecureView.DoesNotExist:
		return HttpResponse("Unknown object requested")


def _list_event(request, objectId, secure_params=None):
	parameters = _choose_parameters(request, secure_params)
	pretty = 'pretty' in parameters
	#print 'pretty is in params'
	if 'format' in parameters and parameters['format']:
		format = parameters['format']
	else:
		format = 'display'	# display means ordinary json for now

	if 'date_limit' in parameters and parameters['date_limit']:
		date_limit = parameters['date_limit']	# this WONT WORK ... we'll need to parse some stuff ... just patching for now
	else:
		# for now we should always be getting here ... as the date_limit param is not yet passed
		date_limit = datetime.date.today() - datetime.timedelta(weeks=1)	# event occured within a week of today
	
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
				time_stamp = datetime.datetime.fromtimestamp(float(request.GET['ts']))
				# PATCH!! ... only show the events that have occured before the 'date_limit'
				events = Event.objects.filter(updated_at__gte=time_stamp, occurred_at__gte=date_limit)
			except ValueError as e:
				#print "We have a value error"
				events = [] #Event.objects.all()
		else:
			# events = Event.objects.all()
			events = Event.objects.filter(occurred_at__gte=date_limit)
		if format == 'map':
			event_json = _prepare_map_json(request, events, secure_params)
		elif format == 'htmlmap':
			event_json = _prepare_html_map_json(request, events, secure_params)
		else:
			event_json = serializers.serialize('json', events, indent=4 if pretty else None, sort_keys=pretty)
		return HttpResponse(event_json, content_type='application/json')

def _prepare_map_json(request, events, secure_params=None):
	parameters = _choose_parameters(request, secure_params)
	pretty = 'pretty' in parameters
	#print 'formating for map!'
	results = []
	for event in events:
		map_event = {}
		map_event['name'] = event.name
		map_event['id'] = event.id
		map_event['type'] = "point"
		map_event['Longitude'] = '%s' % event.location.coords[0]
		map_event['Latitude'] = '%s' % event.location.coords[1]
		map_event['layer_id'] = event.event_type.id
		map_event['report_links'] = [report.link for report in event.reports.all()]
		map_event['event_time'] = event.occurred_at.strftime('%a %b %d, %Y at %I:%M %p')
		results.append(map_event)
	map_result = {
		"timestamp": time.time(),
		"events": results,
	}
	map_json = json.dumps(map_result, indent=4 if pretty else None, sort_keys=pretty)
	return map_json

def _prepare_html_map_json(request, events, secure_params=None):
	parameters = _choose_parameters(request, secure_params)
	pretty = 'pretty' in parameters
	event_groups = {}
	for event in events:
		location_key = u'%s, %s' % (event.location.y, event.location.x)
		event_info = {
			'id': event.id,
			'name': event.name,
			'desc': event.description,
			'type_id': event.event_type.id,
			'occured': event.occurred_at.strftime('%a %b %d, %Y at %I:%M %p'),
		}
		if location_key in event_groups:
			group = event_groups[location_key]
			group['events'].append(event_info)
		else:
			# key is not there yet ... so create it
			new_group = {
				'lat': event.location.y,
				'lng': event.location.x,
				'events': [],
			}
			new_group['events'].append(event_info)
			event_groups[location_key] = new_group

	# data['events'] = mark_safe(simplejson.dumps(event_groups))
	# For now ... hardcode this, but ideally it should be passed in as a GET parameter or something similar
	date_limit = datetime.date.today() - datetime.timedelta(weeks=1)
	all_events = Event.objects.filter(occurred_at__gte=date_limit)
	count_by_type = all_events.values('event_type').annotate(amt=Count('event_type'))
	counts = []
	for event_count in count_by_type:
		new_count = {
			'type_id': event_count['event_type'],
			'count': event_count['amt'],
		}
		counts.append(new_count)

	result = {
		'timestamp': time.time(),
		'groups': event_groups,
		'layer_counts': counts,
	}
	# print events.values('event_type').annotate(amt=Count('event_type'))
	map_json = json.dumps(result, indent=4 if pretty else None, sort_keys=pretty)
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

def basic_search(request):
	pretty = 'pretty' in request.GET
	if 'query' in request.GET and request.GET['query']:
		query = request.GET['query']
		# ideally we'd want to be able to search the location field too ... for now just name and description
		events = Event.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
		search_result = []
		for event in events:
			new_result = {
				'id': event.id,
				'name': event.name,
				'description': event.description,
				'type_id': event.event_type.id,
			}
			search_result.append(new_result)
		
		search_json = json.dumps(search_result, indent=4 if pretty else None, sort_keys=pretty)
		return HttpResponse(search_json, content_type='application/json')
	else:
		search_result = []
		search_json = json.dumps(search_result, indent=4 if pretty else None, sort_keys=pretty)
		return HttpResponse(search_json, content_type='application/json')


