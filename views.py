from django.shortcuts import render_to_response
from django.http import HttpResponse
from mapstream2.stream.models import Event, EventType 	# we may have to build a settings object in the db for the map
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.core import serializers
from theme.models import Theme
from theme.forms import ThemeForm

def home(request):
    return render_to_response('static/map/Main.html')

def map(request):
	data = {}
	# data.update(csrf(request))
	# we want to load the map settings, layers etc from the database from this point and pass it to the template
	event_type_info = []
	for event_type in EventType.objects.all():
		new_info = {
			'id': event_type.id,
			'name': event_type.name,
			'desc':	event_type.description,
			'keywords': event_type.keyword,		# for now just get the main keyword ... later get all the root words
			'colour': event_type.colour,
			'count': event_type.event_set.count(),
		}
		event_type_info.append(new_info)
	data['event_info'] = mark_safe(simplejson.dumps(event_type_info))
	data['raw_info'] = event_type_info

	# events = []
	# for event in Event.objects.all():
	# 	event_info = {
	# 		'id': event.id,
	# 		'name': event.name,
	# 		'desc': event.description,
	# 		'type_id': event.event_type.id,
	# 		'lat': event.location.y,
	# 		'lon': event.location.x,
	# 	}
	# 	events.append(event_info)
	# data['events'] = mark_safe(simplejson.dumps(events))

	event_groups = {}
	for event in Event.objects.all():
		location_key = u'%s, %s' % (event.location.y, event.location.x)
		event_info = {
			'id': event.id,
			'name': event.name,
			'desc': event.description,
			'type_id': event.event_type.id,
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

	data['events'] = mark_safe(simplejson.dumps(event_groups))

	# construct a dummy levels object for now
	levels_info = [
		{
			'id': 0,
			'name': 'Event',
			'max_zoom': 21,
			'colour': '#f5f5f5',
		},
	]
	data['levels'] = mark_safe(simplejson.dumps(levels_info))

	data['refresh_time'] = 30000;
	
	return render_to_response("map.html", data)

def _fetch_events_grouped(time_stamp=None, date_limit=None):
	"""Used by the map request to format the events in groups. Optionally takes a timestamp
	argument that is used to limit the events returned to those occuring after the time
	specified by the timestamp"""
	event_groups = {}
	date_limit = datetime.date.today() - datetime.timedelta(weeks=1)	# event occured within a week of today
	if time_stamp:
		events = Event.objects.filter(updated_at__gte=time_stamp, occurred_at__gte=date_limit)
	else:
		events = Event.objects.filter(occurred_at__gte=date_limit)
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

	data['events'] = mark_safe(simplejson.dumps(event_groups))



def help(request):
	themes = Theme.objects.all()
	form = ThemeForm()
	return render_to_response("help.html", locals())

