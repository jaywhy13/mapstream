# from django.db import models
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import datetime, random, string

# These are the core models of the system

class Tag(models.Model):
	"""Tag object to be used system wide to help categorize objects"""
	name = models.CharField(max_length=255)

	def __unicode__(self):
		return self.name

class Vote(models.Model):
	VOTE_CHOICES = (
		('n', 'No'),
		('y', 'Yes'),
	)
	choice = models.CharField(max_length=1, choices=VOTE_CHOICES, default='n')
	# the user who the vote belongs to. User votes have different weights
	user = models.ForeignKey(User, blank=True, null=True)


class GeoObject(models.Model):
	"""For now this is a MultiPolygon of Communities"""
	community = models.CharField(max_length=40)		# main display name of the field
	parish = models.CharField(max_length=40)
	pop1991_field = models.FloatField()
	pop2001_field = models.FloatField(verbose_name='Population (2001)')
	area = models.FloatField()
	perimeter = models.FloatField()
	acres = models.FloatField()
	hectares = models.FloatField()
	area_sqkm = models.FloatField()

	geom = models.MultiPolygonField()
	centroid = models.PointField(null=True, blank=True)
	objects = models.GeoManager()

	def __unicode__(self):
		return self.community


class EventReport(models.Model):
	title = models.CharField(max_length=255)
	event_type = models.ForeignKey("EventType", blank=True, null=True)
	made_by = models.ForeignKey(User)		# user making the report (incl. system users)
	time_of_report = models.DateTimeField(default=datetime.datetime.now())
	confidence = models.FloatField()	# a percentage ... so 1.0 is 100%
	location = models.PointField(default='POINT(0 0)')
	# eventually reports may contain pictures, audio and even video

	def __unicode__(self):
		return "%s by %s %s" % (self.title, self.made_by, self.time_of_report)


class EventType(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(max_length=500, blank=True, null=True)
	keyword = models.CharField(max_length=255)

	def __unicode__(self):
		return self.name

class EventStatus(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(max_length=500, blank=True, null=True)

	class Meta:
		verbose_name = 'Event status class'
		verbose_name_plural = 'Event status classes'

	def __unicode__(self):
		return self.name


class Event(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(max_length=500, blank=True, null=True)
	event_type = models.ForeignKey("EventType")
	time_created = models.DateTimeField()
	created_by = models.ForeignKey(User)
	status = models.ForeignKey("EventStatus")	# things like: confirmed_by_vote, unconfirmed, invalidated_by_editor etc
	reports = models.ManyToManyField("EventReport")
	votes = models.ManyToManyField("Vote", blank=True)	# user votes on event validity
	# location = models.ForeignKey('GeoObject')	# location - this is a geo_object (can be a point, a polygon etc)

	def __unicode__(self):
		return self.name
	
	def is_open(self):
		hr_before = datetime.datetime.now() - datetime.timedelta(hours=1)
		return self.time_created > hr_before

	def get_location(self):
		# just return (0,0) for now
		lat = 0.0
		lon = 0.0
		return (lat, lon)

	@staticmethod
	def get_open_events():
		hr_before = datetime.datetime.now() - datetime.timedelta(hours=1)
		return Event.objects.filter(time_created__gt=hr_before)

	@staticmethod
	def event_from_report(report):
		"""Given a report, check if it is a part of any event"""
		pass



class UserProfile(models.Model):
	"""This is the core profile of a user in the system"""
	# api_key .. generated key which a user can use to access the system's rest api (when it's built lol)
	pass


def _random_key():
	return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(30))

class SecureView(models.Model):
	key = models.CharField(max_length=255, unique=True, default=_random_key)
	url = models.CharField(max_length=500)
	parameters = models.ManyToManyField("SecureViewParameter", blank=True)

	def __unicode__(self):
		return u"%s -> %s" % (self.key, self.url)
	
	@property
	def view_parameters(self):
		return u', '.join(["%s" % param for param in self.parameters.all()])

class SecureViewParameter(models.Model):
	keyword = models.CharField(max_length=255)
	value = models.TextField(max_length=500, blank=True, null=True)

	def __unicode__(self):
		return u"%s: %s" % (self.keyword, self.value)



# signals
@receiver(post_save, sender=EventReport, dispatch_uid="stream.event_report_created")
def event_report_created(sender, instance, created, **kwargs):
	print "An event (%s) has been reported!!" % instance
	# create a new event here
	location_name = "(location to be determined)"
	new_event = Event()
	new_event.name = "%s happening at %s" % (instance.event_type, location_name)
	new_event.event_type = instance.event_type
	new_event.time_created = datetime.datetime.now()
	new_event.status = EventStatus.objects.get(name="Unconfirmed")
	new_event.created_by = User.objects.get(username="system")
	new_event.save()	# have to call save before trying to add the reports as it is a M2M relationship
	new_event.reports.add(instance)
	new_event.save()




