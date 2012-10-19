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

	@staticmethod
	def create_word(word, type="noun"):
		(word_type, created) = WordType.objects.get_or_create(name=type)
		return Word.objects.create(root=word, word_type=word_type)

	def get_all_forms(self):
		"""Returns a list containing the root word and all the finite_forms"""
		finite_forms = [word.root for word in self.finite_forms.all()]
		result = [self.root]
		result.extend(finite_forms)
		return result


	@staticmethod
	def get_word_chain(text):
		list = Word.get_all_word_forms(text) # all finite forms
		all = list
		for str in list:
			word = Word.get_word(str)
			similar = [ w.root for w in word.similar_words.all() if w.root not in all and w.root != text ]
			finite_forms = [ w.root for w in word.finite_forms.all() if w.root not in all and w.root != text ]
			all.extend(similar)
			all.extend(finite_forms)
		return all
	
	@staticmethod
	def get_all_word_forms(text):
		word = Word.get_word(text)
		if word:
			return word.get_all_forms()
		else:
			return []

	@staticmethod
	def get_word(text, type="noun"):
		(word_type, created) = WordType.objects.get_or_create(name=type)
		matches = Word.objects.filter(root=text, word_type=word_type)
		if len(matches) > 1: # we have duplicate words... delete all but the first
			for match in matches[1:]:
				match.delete()
		(word, created) = Word.objects.get_or_create(root=text, word_type=word_type)
		return word

	



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
