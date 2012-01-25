import os

from mapstream2.listener.models import *
from mapstream2.sherlock.models import *
from mapstream2.stream.models import *
from mapstream2.listener.loader import *
from mapstream2.sherlock.search import *
from mapstream2.listener.greader.googlereader import *
from mapstream2.listener.greader.url import *
from mapstream2.listener.greader.items import *
from mapstream2.listener.greader.auth import *
from mapstream2.listener.tasks import *
from django.contrib.gis.utils import LayerMapping


""" Test the Google Reader functionality """
def runGR():
    ds = DataSource.objects.all()[3] # get the last data source
    gr = GoogleReaderLoader(ds)
    print "calling load on google reader feed"
    gr.load()


""" Test the basic search algorithm """
def runBSA(search_text='A man was found dead on Trafalgar Rd',title='Man found dead on Trafalgar'):
    print "Running basic search algorithm"
    bsa = BasicSearchAlgorithm()

    event_reports = bsa.do_search(search_text = search_text, title=title)
    if(len(event_reports) > 0):
        print " Found %s results" % (len(event_reports))
    else:
        print "No results found, sorry. Hush"
            
def runFba():
    print "Running Facebook Agent"
    fba = FacebookAgent()
    fba.search()


def runGra():
    print "Running Google Reader Agent"
    gra = GoogleReaderAgent()
    gra.search()


def runFbl():
    print "Running Facebook Loader"
    fbl = FacebookLoader()
    fbl.load()


def runFbt():
    fbt = FacebookLoaderTask()
    fbt.delay()


def purgeRaw():
    RawData.objects.all().delete()
    EventReport.objects.all().delete()

def importRoads(shpFileLocation):

    if os.path.exists(shpFileLocation):
        
        road_mapping = {
            'name' : 'NAME',
            'count' : 'COUNT',
            'first_clas' : 'FIRST_CLAS',
            'geom' : 'POINT',
            }
        
        lm = LayerMapping(Road,shpFileLocation,road_mapping,transform=False,encoding='iso-8859-1')
        lm.save(strict=True,verbose=True)
    else:
        print "%s does not exist!" % shpFileLocation
