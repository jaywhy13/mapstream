from celery.decorators import task
from celery.task import Task
from celery.registry import tasks

# custom imports
from listener.loader import FacebookLoader
from listener.models import DataSource, DataSourceType, DataSourceStatus, RawData
from stream.models import Event,EventReport


#@task(name="simplicity")
class SampleTask(Task):
    
    name = "simplicity"

    def run(self, x,y):
        return x + y

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

class PurgeAllTask(Task):
    
    name = "purgeall"
    
    def run(self):
        RawData.objects.all().delete()
        EventReport.objects.all().delete()

tasks.register(SampleTask)
tasks.register(FacebookLoaderTask)
tasks.register(PurgeAllTask)

@task()
def add(x,y):
    return x + y
