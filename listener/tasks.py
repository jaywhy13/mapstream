from celery.decorators import task
from celery.task import Task
from celery.registry import tasks

# custom imports
from listener.loader import FacebookLoader
from listener.models import DataSource, DataSourceType

#@task(name="simplicity")
class SampleTask(Task):
    
    name = "simplicity"

    def run(self, x,y):
        return x + y

class FacebookLoaderTask(Task):

    name = "fbloader"

    def run(self):
        fbtype = DataSourceType.objects.get(name='Facebook')
        data_source_set = DataSource.objects.filter(src_type=fbtype)
        
        for fb_data_source in data_source_set:
            if fb_data_source:
                print "Source is good, lets go"
                fbl = FacebookLoader(data_src=fb_data_source)
                fbl.load()
            else:
                print "We found an empty source"

tasks.register(SampleTask)
tasks.register(FacebookLoaderTask)


@task()
def add(x,y):
    return x + y
