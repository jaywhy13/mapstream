import urllib2
#import libxml2dom
import json
import re
import datetime
from dateutil import parser
from BeautifulSoup import BeautifulSoup

from listener.models import RawData, DataTag, DataSource, DataSourceType
from sherlock.search import FacebookAgent, GoogleReaderAgent
from listener.greader.googlereader import *
from listener.greader.url import *
from listener.greader.items import *
from listener.greader.auth import *


import feedparser
import leaf



class Loader():
	source_type = None

	def load(self, store_data=True):
		pass

	def get_data_sources(self, new_only=True):
		if self.source_type:
			sources = DataSource.objects.filter(src_type=self.source_type)
			return sources
		return None

class FacebookLoader(Loader):
	base_url = 'https://graph.facebook.com'

	def __init__(self, data_src=None, object_id=103093949726983, token='AAADWc1jTVEkBAM00FK9cqwOV8HsD2nJjZBrrnWare1r4Htj4OfzX8fNNbwmU2mACjbxkMHxJjvdtRTgZBOtAczezKOMDIZD'):
		if data_src:
			print "Setup the data source"
			self.object_id = data_src.src_id
			self.data_src = data_src
		else:
			self.object_id = object_id
			print "Could not set the datasource"
		self.token = token
		self.base_url = '%s/%s' % (self.base_url, self.object_id)
		self.source_type = DataSourceType.objects.get(name='Facebook')
	
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
				fblinktype = data.get('type',None)
				new_data = RawData()
				title = data.get('name',data['id'])
				created_at = data.get('created_time',str(datetime.datetime.now()))

				if fblinktype:
					if fblinktype == "link" and data.get('description',None):
						title = data.get('description')
					elif data.get('message',None):
						title = data.get('message')

				if len(title) > 100:
					title = title[:100] + "..."

				new_data.title = title
				new_data.data_id = data['id']
				new_data.source = self.data_src
				new_data.data = json.dumps(data)
				actions = data.get('actions', None)
				if actions:
					new_data.link = actions[0].get('link', None)
				else:
					print "we have no actions!!?"

				# try and parse the date
				try:
					dt = parser.parse(created_at)
				except ValueError:
					dt = datetime.datetime.now()

				new_data.occurred_at = dt
				
				# make sure that the raw data does not exist
				if not new_data.exists():
					new_data.save()
					new_data.tags.add(new_tag)
					new_data.save()
					new_datas.append(new_data)

			if new_datas:
				fba = FacebookAgent()
				fba.search(raw_data_set = new_datas)
			else:
				print "not getting any new data"
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

		# set the src type
		self.source_type = DataSourceType.objects.get(name='GoogleReader')
		
		# check for crucial parameters
		self.username = self.parameters.get('username','adventistvoices@gmail.com')
		self.psw = self.parameters.get('password','choirpassword')
		self.article_css_selector = self.parameters.get('article-css-selector','')
		self.fetch_limit = self.parameters.get('fetch-limit',50)


	def load(self, store_data = True, date_limit=None):
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
						new_data.data = strip_tags(article_html)
						new_data.data_id = item.id
						new_data.link = item.url

						try:
							new_data.occurred_at = datetime.datetime.fromtimestamp(feed.lastUpdated)
						except ValueError:
							print "Error, could not parse timestamp: %s" % feed.lastUpdated
							new_data.occurred_at = datetime.datetime.now()

						# patching in date limit thing Parris wanted --------------------------
						# if date_limit is None:
						#	date_limit = datetime.date.today() - datetime.timedelta(week=1)
						#
						# if new_data.occured_at < date_limit:
						# 	# we should skip this item .... it is too old
						# 	continue
						#
						# end patch -----------------------------------------------------------
						# Abandonning this idea for now ... I think it's best to patch the map view and not mess with this for now

							
						# if it is not new... save it
						if not new_data.exists():
							new_data.save()
							new_data.tags.add(new_tag)
							new_datas.append(new_data)
							fetch_count +=1

						read_items.append(item)


				print "All done.\n %s items fetched, our limit is %s. There are %s feeds. We stopped at index %s" % (fetch_count, self.fetch_limit, len(feed.items),index)

			if new_datas:
				gra = GoogleReaderAgent()
				gra.search(raw_data_set = new_datas)
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
	


def strip_tags(str):
	return ''.join(BeautifulSoup(str).findAll(text=True))

