from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from stream.models import *
from sherlock.models import *

class Theme(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True, null=True)
	colour = models.CharField(max_length="10", default="#5e5e5e")

@receiver(post_save, sender=Theme, dispatch_uid="theme.theme_created")
def theme_created(sender, instance, created, **kwargs):
	if created: # do this only for created stuff 
		# we need to create an event type with that word
		event_types = EventType.objects.filter(name=instance.name)		
		words = Word.objects.filter(root=instance.name)
		
		# check if no such event exists and create it
		if not event_types:
			e = EventType.objects.create(name=instance.name, keyword=instance.name, 
			colour=instance.colour)
		
		# do the same for words
		if not words:
			w = Word.objects.create(root=instance.name)
