from django.db import models

# Create your models here.

class WordType(models.Model):
	"""This represents the role a word plays in the system.
	Eg. root word or finite_form"""
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=255, blank=True, null=True)

	def __unicode__(self):
		return u"%s" % name

class Word(models.Model):
	root = models.CharField(max_length=500)	# word or phrase eg flood, 
	finite_forms = models.ManyToManyField("Word", related_name='word_finite_forms')	# only used if the root has other forms
	similar_words = models.ManyToManyField("Word", related_name='word_similar_words')
	word_type = models.ForeignKey("WordType")

	def __unicode__(self):
		return u"%s" % root

	def get_all_forms(self):
		"""Returns a list containing the root word and all the finite_forms"""
		finite_forms = [word.root for word in self.finite_forms.all()]
		result = [self.root].extend(finite_forms)
		return result

	@staticmethod
	def get_word(text):
		return Word.objects.get(root=text)


class WordCollection(models.Model):
	name = models.CharField(max_length=50, blank=True, null=True)
	description = models.TextField(max_length=255, blank=True, null=True)
	words = models.ManyToManyField("Word")


class Intel(models.Model):
	name = models.CharField(max_length=50, blank=True, null=True)
	description = models.TextField(max_length=255, blank=True, null=True)
	key_word = models.ForeignKey("Word")	# this is the entry point to the intel eg. Flood
	word_collection = models.ForeignKey("WordCollection")
	confidence = models.FloatField()
