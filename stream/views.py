from mapstream2.stream.forms import ReportEventForm
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from mapstream2.stream.models import EventReport, EventType
from django.contrib.auth.models import User

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

