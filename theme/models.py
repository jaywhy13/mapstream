from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from stream.models import *
from sherlock.models import *
from scheduler.models import *


class Theme(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True, null=True)
	colour = models.CharField(max_length="10", default="#5e5e5e")
	event_type = models.ForeignKey(EventType, blank=True, null=True)

	def __unicode__(self):
		return self.name

	def get_events(self):
		""" get events associated with this theme
		"""
		events = []
		event_types = EventTypes.objects.filter(name=self.name)
		if event_types:
			for event_type in event_types:
				events.extend(Event.objects.filter(event_type=event_type))
		return events

	def get_event_reports(self):
		""" get event reports associated with this theme
		"""
		reports = []
		event_types = EventTypes.objects.filter(name=self.name)
		if event_types:
			for event_type in event_types:
				reports.extend(EventReport.objects.filter(event_type=event_type))
		return reports

	def get_task(self):
		tasks = ProjectTask.objects.filter(name="theme_%s" % self.pk, celery_task_name="theme_delegate")
		if tasks:
			return tasks[0]
		return None
	
	@staticmethod
	def create_theme(title, words, colour="#b3c4df", description=None):
		if words:
			# create the theme
			theme = Theme.objects.create(name=title, description=title, colour=colour)

			# Check if we have an event type
			root_word = words[0]
			(event_type, created) = EventType.objects.get_or_create(keyword=root_word, colour=colour)
			if created:
				event_type.colour = colour
				event_type.save()
			theme.event_type = event_type
			
			# Now check Sherlock for the root word, create one if not...
			(word_type, created) = WordType.objects.get_or_create(name="noun")
			(sherlock_word, created) = Word.objects.get_or_create(root=root_word, word_type=word_type)
			if created:
				for word in words:
					if word is root_word: 
						continue
					print "Adding word: %s" % word
					sherlock_word.similar_words.add(Word.create_word(word))
				sherlock_word.save()
			else: # check if all the words are there as similar
				for word in words:
					if word is root_word:
						continue
					if not sherlock_word.similar_words.filter(root=word).count():
						print "Adding word: %s" % word
						sherlock_word.similar_words.add(Word.create_word(word))
				sherlock_word.save()

			theme.save()
			print "Theme created!"

			# now create a task that will check for raw data for this theme 
			# also.. any preferences for data sources???

#Theme.create_theme("Women in society",['women','woman','female'])

@receiver(post_save, sender=Theme, dispatch_uid="theme.theme_created")
def theme_created(sender, instance, created, **kwargs):
	if not created:
		print "A theme was just updated"
	theme = instance

	project_task = theme.get_task()
	
	if not project_task:
		project_task = ProjectTask.objects.create(name="theme_%s" % theme.pk, celery_task_name="theme_delegate")
	project_task.schedule_every(30, 'seconds', [theme.pk])
	

	#ProjectTask.objects.
