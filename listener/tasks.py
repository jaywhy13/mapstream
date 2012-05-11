from celery.decorators import task
from celery.task import Task
from celery.registry import tasks

# custom imports
from listener.loader import *
from listener.models import DataSource, DataSourceType, DataSourceStatus, RawData
from stream.models import Event,EventReport


#@task(name="simplicity")
class SampleTask(Task):
    
    name = "simplicity"

    def run(self, x,y):
        return x + y

class SiteLinkLoaderTask(Task):
    
    name = "slltask"

    def run(self):
        print "Running Site Link Loader Task"
        slltype = DataSourceType.objects.get(name='SiteLinkLoader')
        active = DataSourceStatus.objects.get(name='Available')
        data_source_set = DataSource.objects.filter(src_type=slltype,state=active)
        
        for sll_data_source in data_source_set:
            if sll_data_source:
                print "Loading content from site: %s" % sll_data_source.description
                sll = SiteLinkLoader(data_src=sll_data_source)
                sll.load()
            else:
                print "We found an empty source"



class FacebookLoaderTask(Task):

    name = "fbloadertask"

    def run(self):
        print "Running Facebook Loader Task"
        fbtype = DataSourceType.objects.get(name='Facebook')
        active = DataSourceStatus.objects.get(name='Available')
        data_source_set = DataSource.objects.filter(src_type=fbtype,state=active)
        
        for fb_data_source in data_source_set:
            if fb_data_source:
                print "Loading content from Facebook source: %s" % fb_data_source.description
                fbl = FacebookLoader(data_src=fb_data_source,object_id=fb_data_source.src_id)
                fbl.load()
            else:
                print "We found an empty source"


class GoogleReaderLoaderTask(Task):

    name = "grloadertask"

    def run(self):
        print "Running Google Reader Loader Task"
        grtype = DataSourceType.objects.get(name='GoogleReader')
        active = DataSourceStatus.objects.get(name='Available')
        data_source_set = DataSource.objects.filter(src_type=grtype,state=active)
        
        for gr_data_source in data_source_set:
            if gr_data_source:
                print "Loading content from Google Reader source: %s" % gr_data_source.description
                grl = GoogleReaderLoader(data_src=gr_data_source)
                grl.load()


class LoaderTask(Task):
    name = "loadertask"
    
    def run(self, src_type, active_only = True):
        if active_only:
            data_source_set = DataSource.objects.filter(src_type=fbtype,state=active)
        else:
            data_source_set = DataSource.objects.filter(src_type=fbtype)

        for data_source in data_source_set:
            if data_source:
                print "Loading data from %s source: " % src_type.name
                if src_type.name == "GoogleReader":
                    loader = GoogleReaderLoader(data_src=data_source_set,object_id=data_source.src_id)
                elif src_type.name == "Facebook":
                    loader = FacebookLoader(data_src=fb_data_source,object_id=fb_data_source.src_id)
            
                if loader:
                    loader.load() # load the data source
                else:
                    print "No loader found"
                
                
        

class PurgeAllTask(Task):
    
    name = "purgeall"
    
    def run(self):
        RawData.objects.all().delete()
        EventReport.objects.all().delete()

tasks.register(SampleTask)
tasks.register(FacebookLoaderTask)
tasks.register(GoogleReaderLoaderTask)
tasks.register(PurgeAllTask)
tasks.register(SiteLinkLoaderTask)

@task()
def add(x,y):
    return x + y
