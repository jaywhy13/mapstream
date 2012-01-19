from mapstream2.listener.models import RawData, DataTag
from mapstream2.stream.models import EventReport, EventType
from django.contrib.auth.models import User
import json

class BasicSearchAlgorithm():
	"""This agent does a simple search on RawData objects, tagging them as valid if it finds 'Jamaica' in them."""

	def __init__(self):
		self.sys_user = User.objects.get(username='system')

	def do_search(self, query='Jamaica', search_text = ''):
		"""First pass of basic search algorithm"""
		return search_array(query, search_text)

	def _create_event_report(self):
		"""For now ... creates a basic Flood report"""
		event_report = EventReport()
		event_report.title = 'Sys created report'
		event_report.event_type = EventType.objects.all()[0]	# just use the 1st event type for now
		event_report.made_by = self.sys_user
		event_report.confidence = 0.5
		event_report.save()	# triggers Event creation
		print 'Created new report'
		return event_report

	def search_word(self, query, search_text):
		if query in search_text:
			return _create_event_report()

	def search_array(self, search_terms, search_text):
		results = []
		for term in search_terms:
			if term in search_text:
				report = _create_event_report()
				results.append(report)
		return results


class BasicAgent():
	def search(self, query = 'Jamaica', raw_data_set = None):
		pass
	

class FacebookAgent(BasicAgent):

	def old_search(self, query = 'Jamaica',raw_data_set = None):
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

	def search(self, query=['Jamaica'], raw_data_set=None):
		"""Searches a collection of RawData with terms provided by the query array"""
		new_tag = DataTag.object.get(name='new')
		if not raw_data_set:
			raw_data_set = new_tag.rawdata_set.all()
			
		reports = []
		for raw_data in raw_data_set:
			# look in the description for Jamaica
			data_obj = json.loads(raw_data.data)
			try:
				data_description = data_obj['description']
				bsa = BasicSearchAlgorithm()
				report = bsa.do_search(query,data_description)	#do search returns an array
				if report:
					reports.extend(report)
			except KeyError:
				print 'no description in raw_data #%s - %s\n' % (raw_data.id, raw_data.data)
					

class RssAgent(BasicAgent):
	pass
