from mapstream2.listener.models import RawData, DataTag
from mapstream2.stream.models import EventReport
from django.contrib.auth.models import User
import json

class BasicSearchAlgorithm():
	"""This agent does a simple search on RawData objects, tagging them as valid if it finds 'Jamaica' in them."""

	def __init__(self):
		self.sys_user = User.objects.get(username='system')
		 
		def do_search(self, query='Jamaica', description = ''):
		"""First Pass of basic search
		Simple check to see if the query is found in the description"""
		if query in data_description:
			event_report = EventReport()
			event_report.title = 'Sys created report'
			event_report.made_by = self.sys_user
			event_report.confidence = 0.5
			event_report.save()
			print 'Created new report'
			return event_report



class BasicAgent():
	def search(self, query = 'Jamaica', raw_data_set = None):
		pass
	

class FacebookAgent(BasicAgent):

	def search(self, query = 'Jamaica',raw_data_set = None):

		new_tag = DataTag.objects.get(name='new')

		if not raw_data_set:
			raw_data_set = new_tag.rawdata_set.all()
			
			reports = [] 

			for raw_data in raw_data_set:
				# look in the description for Jamaica
				data_obj = json.loads(raw_data.data)
				try:
					data_description = data_obj['description']
					bsa = BasicSearchAlgorithm()

					report = bsa.do_search(query,data_description)
					if report:
						reports.append(report)

						
				except KeyError:
					print 'no description in raw_data #%s - %s\n' % (raw_data.id, raw_data.data)
					
					
					
class RssAgent(BasicAgent):

	pass


