from mapstream2.listener.models import RawData, DataTag
import json

class BasicSearchAgent():
	"""This agent does a simple search on RawData objects, tagging them as valid if it finds 'Jamaica' in them."""
	
	def do_search(self):
		"""First Pass of basic search
		We fetch all the new raw data and search in them for one of the 14 parishes"""
		valid_event_count = 0
		new_tag = DataTag.objects.get(name='new')
		new_datas = new_tag.rawdata_set.all()
		for raw_data in new_datas:
			# look in the description for Jamaica
			data_obj = json.loads(raw_data.data)
			try:
				data_description = data_obj['description']
				if 'Jamaica' in data_description:
					valid_event_count = valid_event_count + 1
			except KeyError:
				print 'no description in raw_data #%s - %s\n' % (raw_data.id, raw_data.data)
		print "we have %s occurences of Jamaica!" % valid_event_count
