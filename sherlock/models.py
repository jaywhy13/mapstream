from django.db import models

# Create your models here.

class WordType(models.Model):
	"""This represents the role a word plays in the system.
	Eg. root word or finite_form"""
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=255, blank=True, null=True)

	def __unicode__(self):
		return u"%s" % self.name

class Word(models.Model):
	root = models.CharField(max_length=500)	# word or phrase eg flood, 
	finite_forms = models.ManyToManyField("Word", related_name='word_finite_forms',blank=True)	# only used if the root has other forms
	similar_words = models.ManyToManyField("Word", related_name='word_similar_words',blank=True)
	word_type = models.ForeignKey("WordType")
	
	
	@property
	def finite_forms_description(self):
		list = [word.root for word in self.finite_forms.all()]
		return ', '.join(list)

	@property
	def similar_words_description(self):
		list = [word.root for word in self.similar_words.all()]
		return ', '.join(list)


	def __unicode__(self):
		return u"%s" % self.root

	def get_all_forms(self):
		"""Returns a list containing the root word and all the finite_forms"""
		finite_forms = [word.root for word in self.finite_forms.all()]
		result = [self.root]
		result.extend(finite_forms)
		return result

	
	@staticmethod
	def get_all_word_forms(text):
		word = Word.get_word(text)
		if word:
			return word.get_all_forms()
		else:
			return []

	@staticmethod
	def get_word(text):
		try:
			return Word.objects.get(root=text)
		except:
			return None

	



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
