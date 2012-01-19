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

class DataSourceParameter(models.Model):
	"""This model stores extra parameters for the data source such as password"""
	name = models.CharField(max_length=255)
	value = models.TextField(max_length=500)

	def __unicode__(self):
		return u"%s : %s" % (self.name, self.value)

class DataSource(models.Model):
	"""An instance of the datasource type: eg ODPEM facebook feed"""
	src_type = models.ForeignKey("DataSourceType")
	src_id = models.TextField(max_length=500)		# the string tht uniquely id's this source (eg a username/id)
	description = models.TextField(max_length=500, blank=True, null=True)
	date_added = models.DateTimeField(default=datetime.datetime.now())
	state = models.ForeignKey("DataSourceStatus")
	time_last_active = models.DateTimeField(blank=True, null=True)
	parameters = models.ManyToManyField("DataSourceParameter")

	def getParameters(self):
		dict = {}
		for parameter in self.parameters.all():
			dict[parameter.name] = parameter.value
		return dict


	def __unicode__(self):
		return u"%s: %s" % (self.src_type, self.src_id)



class RawData(models.Model):
	title = models.CharField(max_length=255)
	source = models.ForeignKey("DataSource")
	data = models.TextField(blank=True, null=True)
	data_id = models.CharField(max_length=255,blank=True,null=True)
	time_added = models.DateTimeField(default=datetime.datetime.now())
	time_created = models.DateTimeField(default=datetime.datetime.now())
	tags = models.ManyToManyField("DataTag")
	# metadata column ---> more info
	def __unicode__(self):
		return u"%s (%s)" % (self.title, self.source)
