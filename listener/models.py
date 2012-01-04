from django.db import models
import datetime

# Create your models here.

# raw data will be stored in this app

class DataTag(models.Model):
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=255, blank=True, null=True)

	def __unicode__(self):
		return u"%s" % self.name


class DataSourceType(models.Model):
	"""This is the basic type of a data source: RSS, Twitter, Facebook etc"""
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=255, blank=True, null=True)

	def __unicode__(self):
		return u"%s" % self.name


class DataSourceStatus(models.Model):
	"""The status of a data source: Available, In-use, Unavailable etc"""
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=255, blank=True, null=True)

	def __unicode__(self):
		return u"%s" % self.name


class DataSource(models.Model):
	"""An instance of the datasource type: eg ODPEM facebook feed"""
	src_type = models.ForeignKey("DataSourceType")
	src_id = models.TextField(max_length=500)		# the string tht uniquely id's this source (eg a username/id)
	description = models.TextField(max_length=500, blank=True, null=True)
	date_added = models.DateTimeField(default=datetime.datetime.now())
	state = models.ForeignKey("DataSourceStatus")
	time_last_active = models.DateTimeField(blank=True, null=True)

	def __unicode__(self):
		return u"%s: %s" % (self.src_type, self.src_id)


class RawData(models.Model):
	title = models.CharField(max_length=50)
	source = models.ForeignKey("DataSource")
	data = models.TextField(blank=True, null=True)
	time_added = models.DateTimeField(default=datetime.datetime.now())
	tags = models.ManyToManyField("DataTag")
	# metadata column ---> more info
	def __unicode__(self):
		return u"%s (%s)" % (self.title, self.source)
