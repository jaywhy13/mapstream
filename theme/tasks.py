from celery.decorators import task
from celery.task import Task
from celery.registry import tasks



# custom imports
from listener.loader import *
from listener.models import DataSource, DataSourceType, DataSourceStatus, RawData
from stream.models import Event,EventReport
from sherlock.search import get_class, BasicAgent, GazetteerSearchAlgorithm
from theme.models import Theme

class ThemeDelegate(Task):
	""" This task will be responsible for getting the ball rolling for finding 
	    information for this task
	"""
	name = "theme_delegate"

	def run(self):
		print "This run got called"

	def run(self, theme_id):
		if theme_id:
			try:
				theme = Theme.objects.get(pk=theme_id)
				event_type = theme.event_type
				event_types = [event_type] if event_type else []
				print "Calling basic agent to search for theme: %s" % theme
				gsa = GazetteerSearchAlgorithm()
				ba = BasicAgent()
				reports = ba.search(event_types=event_types, algorithm=gsa)
				if reports:
					print "We found %s reports based on our theme %s" % (len(reports), theme)
				else:
					print "No reports found for our theme %s" % theme
			except Theme.DoesNotExist:
				print "No theme exists with id %s" % theme_id


tasks.register(ThemeDelegate)
