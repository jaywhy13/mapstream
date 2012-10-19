from django.core.management.base import BaseCommand, CommandError
from listener.models import *
from listener.loader import *
from sherlock.search import *
from nltk import FreqDist, ConditionalFreqDist
import nltk

class Command(BaseCommand):
    args = ''
    help = 'Analyzes our raw data'

    def handle(self, *args, **options):
    	fdist = FreqDist()
    	print "Analyzing raw data"
    	limit = 10
    	if args:
    		raw_datas = RawData.objects.filter(pk__in=args)
    	else:
	   		raw_datas = RawData.objects.all()[:limit]
    	tagged_data = []
    	for raw_data in raw_datas:
    		words = nltk.word_tokenize(raw_data.data)
    		tagged_data.extend(nltk.pos_tag(words))
    		for word in words:
    			word = word.strip()
    			if word:
	    			fdist.inc(word)

    	print "Anaylzed %s items" % len(raw_datas)
    	print

    	print "Top word: %s" % fdist.max()
    	print 

    	print "Top 10 words"
    	for word in fdist.keys()[:10]:
    		times = fdist[word]
    		print " -- %s occurred %s times" % (word, times)
    	print

    	
    	print "Bottom 10 words"
    	for word in fdist.keys()[-10:]:
    		times = fdist[word]
    		print " -- %s occurred %s times" % (word, times)
    	print

    	print "Words occurring between 50-100 times"
    	words = [ word for word in fdist.keys() if fdist[word] >= 50 and fdist[word] <= 100 ]
    	print ", ".join(words)


    	cfdist = ConditionalFreqDist()
    	for (word, tag) in tagged_data:
    		cfdist[tag].inc(word)
    	
    	print "Most popular noun: %s" % cfdist["NN"].max()
    	print 

    	print "Top 50 nouns"
    	for word in cfdist["NN"].keys()[:50]:
    		times = cfdist["NN"][word]
    		print " -- %s occurred %s times" % (word, times)
    	print



    