import os

from listener.models import *
from sherlock.models import *
from stream.models import *
from listener.loader import *
from sherlock.search import *
from listener.greader.googlereader import *
from listener.greader.url import *
from listener.greader.items import *
from listener.greader.auth import *
from listener.tasks import *
from django.contrib.gis.utils import LayerMapping





""" Test the Google Reader functionality """
def runGR(run_agent=False):

    print "Running Google Reader Loader Task"
    grtype = DataSourceType.objects.get(name='GoogleReader')
    active = DataSourceStatus.objects.get(name='Available')
    data_source_set = DataSource.objects.filter(src_type=grtype,state=active)
    
    for gr_data_source in data_source_set:
        if gr_data_source:
            print "Loading content from Google Reader source: %s" % gr_data_source.description
            grl = GoogleReaderLoader(data_src=gr_data_source)
            new_datas = grl.load()
            print "Saved %s new raw data items" % len(new_datas)

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


def importSettlements(shpFileLocation):
    if os.path.exists(shpFileLocation):
        geo_mapping = {
            'community' : 'COMMUNITY',
            'parish' : 'PARISH',
            'pop1991_field' : 'POP1991_',
            'pop2001_field' : 'POP2001_',
            'area' : 'AREA',
            'perimeter' : 'PERIMETER',
            'acres' : 'ACRES',
            'hectares' : 'HECTARES',
            'area_sqkm' : 'Area_sqkm',
            'geom' : 'MULTIPOLYGON',
        }
        lm = LayerMapping(GeoObject, shpFileLocation, geo_mapping, transform=False, encoding='iso-8859-1')
        lm.save(strict=True, verbose=True)
    else:
        print "%s does not exist!" % shpFileLocation
