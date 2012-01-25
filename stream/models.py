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
	area_sqkm = models.FloatField(blank=True,null=True)

	geom = models.MultiPolygonField()
	objects = models.GeoManager()

	def __unicode__(self):
		return self.community

class Road(models.Model):
    name = models.CharField(max_length=19)
    count = models.FloatField()
    first_clas = models.CharField(max_length=75)
    geom = models.PointField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
	    return self.name


class EventReport(models.Model):
	title = models.CharField(max_length=255)
	event_type = models.ForeignKey("EventType", blank=True, null=True)
	made_by = models.ForeignKey(User)		# user making the report (incl. system users)
	time_of_report = models.DateTimeField(default=datetime.datetime.now())
	confidence = models.FloatField()	# a percentage ... so 1.0 is 100%
	location = models.PointField(default='POINT(0 0)')
	# eventually reports may contain pictures, audio and even video

	def get_matching_events(self):
		result = []
		events = Event.objects.filter(event_type = self.event_type)
		event_type = self.event_type
		for event in events:
			if event.location and self.location:
				distance = event.location.distance(self.location)
				if distance < event_type.distance_threshold and event.name == self.title:
					result.append(event)
			else:
				print "No location information available for: %s" % event
					
		return result
				
	def has_matching_events(self):
		return len(self.get_matching_events()) > 0


	def __unicode__(self):
		return "%s by %s %s" % (self.title, self.made_by, self.time_of_report)


class EventType(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(max_length=500, blank=True, null=True)
	keyword = models.CharField(max_length=255)
	distance_threshold = models.FloatField(default=0) # distance in meters, 0 for none
	report_threshold = models.IntegerField(default=-0) # report threshold, 0 to disregard (in seconds)
	
	def has_distance_threshold(self):
		return self.distance_threshold > 0

	def has_report_threshold(self):
		return self.time_threshold > 0
	

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
	updated_at = models.DateTimeField(default=datetime.datetime.now())
	status = models.ForeignKey("EventStatus")	# things like: confirmed_by_vote, unconfirmed, invalidated_by_editor etc
	reports = models.ManyToManyField("EventReport")
	votes = models.ManyToManyField("Vote", blank=True)	# user votes on event validity
	location = models.PointField(default='POINT(0 0)')	# location - this is a geo_object (can be a point, a polygon etc)

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



class GeoLocation(models.Model):
	classname = models.CharField(max_length=255)
	search_field = models.CharField(max_length=255)


# signals
@receiver(post_save, sender=EventReport, dispatch_uid="stream.event_report_created")
def event_report_created(sender, instance, created, **kwargs):
	# first check to see if the event has already been reported
	print "  ** Trigger called... post save report"
	if instance.has_matching_events():
		print " >> This event already has matching events. Will update number of reports for this event..."
		for event in instance.get_matching_events():
			event.reports.add(instance)
			event.updated_at = datetime.datetime.now()
			event.save()
	else:
		print "  ** An event (%s) has been reported!!" % instance
		# create a new event here
		location_name = "(location to be determined)"
		new_event = Event()
		new_event.name = "%s happening at %s" % (instance.event_type, location_name)
		new_event.name = instance.title
		new_event.event_type = instance.event_type
		new_event.time_created = instance.time_of_report
		new_event.status = EventStatus.objects.get(name="Unconfirmed")
		new_event.created_by = User.objects.get(username="system")
		new_event.location = instance.location
		new_event.save()	# have to call save before trying to add the reports as it is a M2M relationship
		new_event.reports.add(instance)
		new_event.save()
		print " >> New event created"
	print




