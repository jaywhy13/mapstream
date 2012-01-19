import urllib2
#import libxml2dom
import json
from mapstream2.listener.models import RawData, DataTag
from mapstream2.sherlock.search import FacebookAgent
from mapstream2.listener.greader.googlereader import *
from mapstream2.listener.greader.url import *
from mapstream2.listener.greader.items import *
from mapstream2.listener.greader.auth import *

import feedparser
import leaf

class Loader():
	def load(self, store_data=True):
		pass


class FacebookLoader(Loader):
	base_url = 'https://graph.facebook.com'

	def __init__(self, data_src=None, object_id=103093949726983, token='AAADWc1jTVEkBAM00FK9cqwOV8HsD2nJjZBrrnWare1r4Htj4OfzX8fNNbwmU2mACjbxkMHxJjvdtRTgZBOtAczezKOMDIZD'):
		if data_src:
			print "Setup the data source"
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

	def load(self, store_data=True):
		self.load_feed(store_data)
		

	
	def load_feed(self, store_data=True):
		working_url = self._get_working_url('feed')
		print 'loading feed from: %s' % working_url
		# try:
		f = urllib2.urlopen(working_url)
		print f.info()
		data = f.read()
		# print data
		# try to decode the json string
		json_obj = json.loads(data)
		# print '\n\n--------------------\n%s' % json_obj['data'][0]
		
		if store_data:
			# store the data in the raw_data model
			new_tag = DataTag.objects.get(name='new')
			new_datas = []
			for data in json_obj['data']:
				new_data = RawData()
				new_data.title = data.get('name',data['id'])
				new_data.data_id = data['id']
				new_data.source = self.data_src
				new_data.data = json.dumps(data)
				new_data.save()
				new_data.tags.add(new_tag)
				new_data.save()
				new_datas.append(new_data)
			fba = FacebookAgent()
			fba.search(raw_data_set = new_datas)
		# except HttpError:
		# 	print 'Seems like the token has expired ... fetch a new one'
	
	
	def request_new_token(self):
		"""Fetches a new OAUTH token for use with the Facebook Graph API"""
		pass



class GoogleReaderLoader(Loader):

	def __init__(self, data_src):
		self.url = data_src.src_id
		self.source_node = data_src
		self.parameters = data_src.getParameters()
		
		# check for crucial parameters
		self.username = self.parameters.get('username','adventistvoices@gmail.com')
		self.psw = self.parameters.get('password','choirpassword')
		self.article_css_selector = self.parameters.get('article-css-selector','')
		self.fetch_limit = self.parameters.get('fetch-limit',50)


	def load(self, store_data = True):
		print "Connecting as %s" % self.username
		auth = ClientAuthMethod(self.username,self.psw)
		
		reader = GoogleReader(auth)
		if reader.buildSubscriptionList():
			feeds = reader.getSubscriptionList()
			new_tag = DataTag.objects.get(name='new')
			new_datas = []
			fetch_count = 0

			# loop through and store feeds we already have RawData for


			for feed in feeds:
				read_items = []
				print "Reading " + feed.title + " (%s unread)" % feed.unread
				print "===================================================="
				print
				print "Loading items"
				print
				feed.loadItems()
				print "Loaded %s items" % (len(feed.items),)
				print
				index = 0
				for item in feed.items:
					# make sure it doesn't already exist
					title = item.title
					url = item.url
					index+=1

					if index + 1 >= len(feed.items) and fetch_count < self.fetch_limit:
						print "Loading more items...."
						print
						feed.loadMoreItems()

					if len(RawData.objects.filter(data_id=item.id,source=self.source_node)) > 0 or item in read_items:
						print "   Skipping %s, we already saved it." % title
						continue

					f = urllib.urlopen(url)
					html = f.read()
					doc = leaf.parse(html)
					elements = doc(self.article_css_selector)
					for element in elements:
						print " + Saving article: %s" % title
						print
						article_html = element.html()
						new_data = RawData()
						new_data.title = title
						new_data.source = self.source_node
						new_data.data = article_html
						new_data.data_id = item.id
						new_data.save()
						new_data.tags.add(new_tag)
						new_datas.append(new_data)
						read_items.append(item)
						fetch_count +=1

				print
				print "All done.\n %s items fetched, our limit is %s. There are %s feeds. We stopped at index %s" % (fetch_count, self.fetch_limit, len(feed.items),index)

			return new_datas
		return None
				
	



class RssLoader(Loader):

	def __init__(self, data_src):
		self.url = data_src.src_id
		self.source_node = data_src

	def fetch_data(self):
		""" Override fetch data of parent
		Uses the feedparser library to fetch the contents of an RSS feed from a given url. The entries in the
		result are then used to create a new RawData object."""
		data = feedparser.parse(self.url)
		print data
		# add data to 'RawData table'
		for entry in data.entries:
			rd = RawData()
			rd.title = entry.title
			rd.data = entry
			rd.source = self.source_node
			rd.save()
		return data


	def load(self, store_data = True):
		self.fetch_data()
	
