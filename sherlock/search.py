from mapstream2.listener.models import RawData, DataTag, DataSource, DataSourceType, DataSourceStatus
from mapstream2.stream.models import EventReport, EventType, GeoLocation
from mapstream2.sherlock.models import *
from django.contrib.auth.models import User


import json


class BasicSearchAlgorithm():
	"""This agent does a simple search on RawData objects, tagging them as valid if it finds 'Jamaica' in them."""

	def __init__(self):
		self.sys_user = User.objects.get(username='system')

	def do_search(self, search_text = None, title = None, raw_data = None):

		"""First pass of basic search algorithm"""
		#search_text = search_text.lower()
		# loop over our location

		#print "Running basic search on text: %s" % title

		locations = GeoLocation.objects.all() # need to do heirarchical search, parish then community
		event_types = EventType.objects.all()
		reports = []
		
		if not search_text:
			return reports
		
		for location in locations:
			classname = location.classname
			search_field = location.search_field
			try:
				model_instance = get_class(classname)
				models = model_instance.objects.all()

				for model in models:
					geotitle = eval('model.' + search_field + '.strip().title()')

					if not geotitle:
						continue

					if geotitle in search_text:
						for event_type in event_types:
							# print "    Searching for event type: %s (keyword=%s)" % (event_type,event_type.keyword)
							if event_type.keyword:
								words = Word.get_all_word_forms(event_type.keyword)
								# print "     - Will search in %s" % [word for word in words]
								for word in words:
									# print "     Searching text for %s" % word
									if word in search_text:
										print " ++ Matched word: %s in %s" % (word,geotitle)
										report = self._create_event_report()
										if title:
											if geotitle not in title:
												title = title + " (" + geotitle + ")"
											report.title = title


										report.event_type = event_type
										report.location = model.geom.centroid
										if raw_data:
											report.occurred_at = raw_data.occurred_at
											report.link = raw_data.link

										# only save the report if it doesn't exist
										if not report.exists():
											report.save()
											reports.append(report)
											
			except Exception as e:
				print "ERROR: %s" % e
		return reports
		# return search_array(search_text)

	def _create_event_report(self):
		"""For now ... creates a basic Flood report"""
		event_report = EventReport()
		event_report.title = 'Sys created report'
		event_report.event_type = EventType.objects.all()[0]	# just use the 1st event type for now
		event_report.made_by = self.sys_user
		event_report.confidence = 0.5
		#event_report.save()	# triggers Event creation
		#print ' >> Created new report'
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
	def search(self, raw_data_set = None):
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
				#print 'no description in raw_data #%s - %s\n' % (raw_data.id, raw_data.data)
				pass

	def search(self, raw_data_set=None):
		"""Searches a collection of RawData with terms provided by the query array"""
		new_tag = DataTag.objects.get(name='new')
		
		fb_data_source_type = DataSourceType.objects.get(name='Facebook')
		active = DataSourceStatus.objects.get(name='Available')
		fb_data_sources = DataSource.objects.filter(src_type=fb_data_source_type,state=active)

		if not raw_data_set:
			raw_data_set = new_tag.rawdata_set.filter(source__in=fb_data_sources)
			
		all_reports = []
		#print "Will search %s Facebook sources" % len(raw_data_set)

		for raw_data in raw_data_set:
			# look in the description for Jamaica
			data_obj = json.loads(raw_data.data)
			fbtype = data_obj["type"]
			data_description = None

			# if its a link, check description. Check message otherwise. 
			if fbtype == "link":
				data_description = data_obj.get('description',None)
				# Need to follow links eventually
			else:
				data_description = data_obj.get('message',None)

			bsa = BasicSearchAlgorithm()
			try:
				title = data_obj.get('title',data_description)
				if title and len(title) > 100:
					title = title[:100] + "..."

				reports = bsa.do_search(search_text = data_description, title = title, raw_data = raw_data)	#do search returns an array
				if reports:
					all_reports.extend(reports)
			except KeyError as e:
				#print 'no description in raw_data #%s - %s\n' % (raw_data.id, raw_data.data)
				pass
					

class RssAgent(BasicAgent):
	pass


class GoogleReaderAgent(BasicAgent):
	def search(self, raw_data_set = None):

		new_tag = DataTag.objects.get(name='new')
		
		gr_data_source_type = DataSourceType.objects.get(name='GoogleReader')
		gr_data_sources = DataSource.objects.filter(src_type=gr_data_source_type)

		if not raw_data_set:
			raw_data_set = new_tag.rawdata_set.filter(source=gr_data_sources)
			
		all_reports = []
		for raw_data in raw_data_set:
			# look in the description for Jamaica
			bsa = BasicSearchAlgorithm()
			try:
				search_text = raw_data.data
				title = raw_data.title
				reports = bsa.do_search(search_text = search_text, title = title, raw_data = raw_data)	#do search returns an array
				if reports:
					all_reports.extend(reports)
			except KeyError as e:
				#print e
				pass



def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m
