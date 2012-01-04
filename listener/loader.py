import urllib2
import json
from mapstream2.listener.models import RawData, DataTag

class FacebookLoader():
	base_url = 'https://graph.facebook.com'

	def __init__(self, data_src=None, object_id=103093949726983, token='AAADWc1jTVEkBAM00FK9cqwOV8HsD2nJjZBrrnWare1r4Htj4OfzX8fNNbwmU2mACjbxkMHxJjvdtRTgZBOtAczezKOMDIZD'):
		if data_src:
			self.object_id = data_src.src_id
			self.data_src = data_src
		else:
			self.object_id = object_id
		self.token = token
		self.base_url = '%s/%s' % (self.base_url, self.object_id)

	
	def _get_working_url(self, data_type):
		default = 'Data type "%s" is unsupported' % data_type
		results = {
			'feed': '%s/%s' % (self.base_url, 'feed'),
			'notes': '%s/%s' % (self.base_url, 'notes'),
		}
		url = results.get(data_type, default)
		if self.token:
			url = '%s?access_token=%s' % (url, self.token)
		# else:
			# do some stuff to fecth a valid token and set it
		return url

	
	def load_feed(self, store_data=True):
		working_url = self._get_working_url('feed')
		print 'loading feed from: %s' % working_url
		# try:
		f = urllib2.urlopen(working_url)
		print f.info()
		data = f.read()
		print data
		# try to decode the json string
		json_obj = json.loads(data)
		print '\n\n--------------------\n%s' % json_obj['data'][0]
		
		if store_data:
			# store the data in the raw_data model
			new_tag = DataTag.objects.get(name='new')
			for data in json_obj['data']:
				new_data = RawData()
				new_data.title = data['id']
				new_data.source = self.data_src
				new_data.data = json.dumps(data)
				new_data.save()
				new_data.tags.add(new_tag)
				new_data.save()
		# except HttpError:
		# 	print 'Seems like the token has expired ... fetch a new one'
	
	
	def request_new_token(self):
		"""Fetches a new OAUTH token for use with the Facebook Graph API"""
		pass
