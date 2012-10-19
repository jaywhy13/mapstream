from listener.models import RawData, DataTag, DataSource, DataSourceType, DataSourceStatus
from stream.models import EventReport, EventType, GeoLocation, Gazetteer
from sherlock.models import *
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry

import json


class GazetteerSearchAlgorithm():
	""" This agent does a smart search on RawData objects...
	"""
	name = "Gazetteer Search Algorithm"

	def __init__(self):
		self.sys_user = User.objects.get(username='system')

	def do_search(self, search_text = None, title = None, raw_data = None, limit=5, event_types=None):
		reports = []

		if not search_text:
			return reports

		threshold = 60
		
		weightings = {}

		if event_types is None:
			event_types = EventType.objects.all()

		#print "Searching gazetteer for places in %s" % title

		# start searching each level
		start_level = 0
		end_level = 5

		# read in the common list of words
		f = open("data/words.txt")
		common_words = []
		if f:
			txt = f.read()
			common_words = txt.split('\n')
		for event_type in event_types:
			#print "Searching for occurence of event: %s" % event_type
			weightings = {}
			words = Word.get_word_chain(event_type.keyword) # use word chain instead
			for word in words:
				if word not in search_text:
					continue

				#print " Found occurrence of %s in text" % word
				
				for i in range(start_level,end_level):
					level_weightings = {}
					places = Gazetteer.objects.filter(level=i)
							
					for place in places:
						if place.search(search_text): # search text for occurrence
							#print " Match found in %s (Place: %s, Word: %s, Level: %s)" % (title, place.name, word, i)
							weighting = place.weighting

							# =======================================================
							# WEIGHTING CALCULATIONS
							# =======================================================

							# minus 30 for common words
							if place.name.lower() in common_words:
								weighting -= 30

							# add weighting based on occurrence
							search_text_occurrences = place.count_occurrences(search_text)
							weighting += 5 * search_text_occurrences
							#if search_text_occurrences:
							#	print " Adding search text occurrence: %s" % search_text_occurrences * 5


							# add wieghting based on occurrence in the title
							title_occurrences = place.count_occurrences(title)
							weighting += 30 * title_occurrences
							#if title_occurrences:
							#	print " Adding title occurrence: %s" % title_occurrences * 30


							# calculate the weighting based on proximity to the previous level
							if i > start_level:
								total_distance = 0
								lower_level_weightings = weightings.get(i-1, [])
								within_lower_level = 0
								distance_penalty = 0
								for pk in lower_level_weightings:
									lower_level_place = Gazetteer.objects.get(pk=pk)
									results = Gazetteer.objects.filter(pk=place.pk).distance(lower_level_place.geom)
									dist = results[0].distance.m / 1000.0 # in km
									total_distance += dist

									#print " Distance from %s to %s is %s" % (place.name, lower_level_place.name, dist)
									# minus the distance in km from the weighting 
									if i == 1: # previous level is country
										distance_penalty += 80 if total_distance > 250 else 0 
									elif i == 2: # previous level is parish
										# minus 10 for every 30km out
										distance_penalty += 10 * total_distance / 30
										if dist < 50:
											within_lower_level = True
											weighting += lower_level_place.weighting / 2										
											#print " Distance plus %s" % (lower_level_place.weighting / 2)
								if not within_lower_level:
									weighting = weighting - distance_penalty
									#print " Distance pentalty is %s" % distance_penalty

							level_weightings[place.pk] = weighting
					
					# now minus the km distance from the centroid
					place_ids = [place.pk for place in places]
					bbox = Gazetteer.objects.filter(pk__in=place_ids).extent() if place_ids else None

					if bbox:
						centroid = GEOSGeometry("POINT (%s %s)" % ((bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2))
						for place_pk in level_weightings:
							weighting = level_weightings.get(place_pk)
							place = Gazetteer.objects.get(pk=place_pk)
							distance_to_centroid = place.geom.distance(centroid)
							#print "Applying weight diff %s" % distance_to_centroid
							#weighting = weighting - (distance_to_centroid/1000)
							level_weightings[place_pk] = weighting

					# update the weightings
					weightings[i] = level_weightings

				# now lets figure out the highest level we have results for...
				for i in reversed(range(start_level, end_level)):

					level_weightings = weightings.get(i, {})
					if level_weightings:
						# group these into a list of tuples (place, weighting)  so we can sort them
						tuple_listing = [ (place_pk, level_weightings[place_pk]) for place_pk in level_weightings ]
						def comp(x, y):
							if x[1] > y[1]:
								return -1
							elif x[1] < y[1]:
								return 1
							else:
								return 0
						tuple_listing.sort(comp)
						# now only create reports for the top limit places
						top_places = tuple_listing
						reports_saved = 0
						#print " Saving top places"
						for (top_place_pk, weighting) in top_places:
							try:
								top_place = Gazetteer.objects.get(pk=top_place_pk)
							except Gazetteer.DoesNotExist:
								continue

							if weighting < threshold:
								print " - Discarding %s with weighting of %s" % (top_place.name, weighting)
								continue
							print " + Keeping %s with weighting of %s" % (top_place.name, weighting)

							report = create_event_report()
							if title:
								report.title = title + " (" + top_place.name + ")"
							
							report.event_type = event_type
							report.location = top_place.geom.centroid
							if raw_data:
								report.occurred_at = raw_data.occurred_at
								report.link = raw_data.link

							# only save the report if it doesn't exist
							if not report.exists():
								print " >> Saving report: %s (Weighting: %s, Level: %s) " % (report.title, weighting, top_place.level)
								report.save()
								reports.append(report)
								reports_saved = reports_saved + 1
							
							if reports_saved >= limit:
								break
						break # don't do any levels lower than this one

		return reports


class BasicSearchAlgorithm():
	"""This agent does a simple search on RawData objects, tagging them as valid if it finds 'Jamaica' in them."""

	name = "Basic Serach Algorithm"

	def __init__(self):
		self.sys_user = User.objects.get(username='system')

	def do_search(self, search_text = None, title = None, raw_data = None, event_types=None):

		"""First pass of basic search algorithm"""
		#search_text = search_text.lower()
		# loop over our location

		print "Running basic search on text: %s" % title

		locations = GeoLocation.objects.all() # need to do heirarchical search, parish then community
		if not event_types:
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
							# TODO: Ensure that this checks all the constraints of each event type
							print "    Searching for event type: %s (keyword=%s)" % (event_type,event_type.keyword)
							if event_type.keyword:
								#words = Word.get_all_word_forms(event_type.keyword)
								words = Word.get_word_chain(event_type.keyword) # use word chain instead
								print "     - Will search in %s" % [word for word in words]
								for word in words:
									# print "     Searching text for %s" % word
									if word in search_text:
										#print " ++ Matched word: %s in %s" % (word,geotitle)
										report = self._create_event_report()
										if title:
											report.title = title + " (" + geotitle + ")"
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
				#print "ERROR: %s" % e
				pass
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
	def search(self, raw_data_set = None, algorithm=None, event_types=None):
		print "Basic agent asked to search..."
		if not raw_data_set:
			print "Will use ALL raw data"
			raw_data_set = RawData.objects.all()

		if not algorithm:
			algorithm = BasicSearchAlgorithm()

		print "Will use %s" % algorithm.name

		all_reports = []
		if raw_data_set:
			for raw_data in raw_data_set:
				title = raw_data.title
				search_text = raw_data.data
				#print "Invoking %s on %s" % (algorithm.name, title)
				reports = algorithm.do_search(search_text = search_text, title = title, raw_data = raw_data, event_types=event_types)	

				if reports:
					all_reports.extend(reports)
		else:
			print "No raw data for Basic agent to search"
		return all_reports

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
		#print "Searching facebook raw data"
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
				title = data_obj.get('title', raw_data.title)
				# title = data_obj.get('title',None) # not sure if we neeed this
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

def create_event_report():
	"""For now ... creates a basic event report
	"""
	event_report = EventReport()
	event_report.title = 'Sys created report'
	(sysuser, created) = User.objects.get_or_create(username="system")
	event_report.made_by = sysuser
	event_report.confidence = 0.5
	return event_report



def get_class( kls, args = None ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    if args:
	    return m(args)
    return m
